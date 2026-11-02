"""Early source-input contract checks for configured authored model jobs.

These checks pin authored selectors to the exact model shards before the
native generator build starts. They do not establish runtime activation or
consumer compatibility; the native generator remains the producer authority.
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path, PurePosixPath
import stat
import sys
import tempfile
import unittest
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "release-contract"))

import native_generation


SELECTOR_FIELDS = {
    "package",
    "module",
    "toolchain",
    "artifact_sha256",
    "targets",
    "configurations",
}
IDENTITY_VALUE_FIELDS = {"name", "version"}
SHA256_LENGTH = 64
AUTHORED_KIND = "authored_semantic_model"
MIN_MODEL_SCHEMA_VERSION = 8
MAX_MODEL_SCHEMA_VERSION = 17


class SourceInputError(ValueError):
    """An invalid authored selector or shard-pin source contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceInputError(message)


def _load_json_bytes(data: bytes, description: str) -> Any:
    """Use the native runner's duplicate-key-rejecting JSON reader."""
    try:
        return native_generation._load_json(data, description)
    except native_generation.NativeGenerationError as error:
        raise SourceInputError(str(error)) from error


def _load_json(relative: str) -> Any:
    path = ROOT / relative
    return _load_json_bytes(path.read_bytes(), relative)


def _normalize_selector(value: Any, description: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{description} must be an object")
    _require(
        set(value) <= SELECTOR_FIELDS,
        f"{description} contains unknown selector fields: {sorted(set(value) - SELECTOR_FIELDS)}",
    )

    normalized: dict[str, Any] = {}
    for field in ("package", "module", "toolchain"):
        identity = value.get(field)
        if identity is None:
            normalized[field] = None
            continue
        _require(isinstance(identity, dict), f"{description}.{field} must be an object or null")
        _require(
            set(identity) <= IDENTITY_VALUE_FIELDS,
            f"{description}.{field} contains unknown fields: {sorted(set(identity) - IDENTITY_VALUE_FIELDS)}",
        )
        name = identity.get("name")
        version = identity.get("version")
        _require(isinstance(name, str) and bool(name), f"{description}.{field}.name must be nonempty")
        _require(
            version is None or (isinstance(version, str) and bool(version)),
            f"{description}.{field}.version must be a nonempty string or null",
        )
        normalized[field] = {"name": name, "version": version}

    artifact_sha256 = value.get("artifact_sha256")
    _require(
        artifact_sha256 is None
        or (
            isinstance(artifact_sha256, str)
            and len(artifact_sha256) == SHA256_LENGTH
            and all(character in "0123456789abcdef" for character in artifact_sha256)
        ),
        f"{description}.artifact_sha256 must be a lowercase SHA-256 digest or null",
    )
    normalized["artifact_sha256"] = artifact_sha256

    for field in ("targets", "configurations"):
        items = value.get(field, [])
        _require(isinstance(items, list), f"{description}.{field} must be an array when present")
        _require(
            all(isinstance(item, str) and item for item in items),
            f"{description}.{field} entries must be nonempty strings",
        )
        # Preserve source order and every nonempty value. Selector arrays are
        # intentionally not sorted or deduplicated by this check.
        normalized[field] = list(items)

    return normalized


def _normalize_selector_vector(value: Any, description: str) -> list[dict[str, Any]]:
    _require(isinstance(value, list) and bool(value), f"{description} must be a nonempty array")
    return [
        _normalize_selector(selector, f"{description}[{index}]")
        for index, selector in enumerate(value)
    ]


def _validate_authored_model_source(spec: Any, model: Any, description: str) -> None:
    _require(isinstance(spec, dict), f"{description} spec must be an object")
    _require(isinstance(model, dict), f"{description} model must be an object")
    _require(type(spec.get("schema_version")) is int, f"{description} schema_version must be an integer")
    schema_version = spec["schema_version"]
    _require(schema_version in (1, 2), f"{description} uses an unsupported authored spec schema")

    kind = spec.get("kind")
    _require(isinstance(kind, dict), f"{description} kind must be an object")
    _require(kind.get("artifact_kind") == AUTHORED_KIND, f"{description} is not an authored semantic model")
    _require(
        set(kind) <= {"artifact_kind", "shard_activation_pins"},
        f"{description} kind contains unknown fields: {sorted(set(kind) - {'artifact_kind', 'shard_activation_pins'})}",
    )

    pins_present = "shard_activation_pins" in kind
    if pins_present:
        _require(schema_version == 2, f"{description} shard_activation_pins require schema_version 2")
        pins = kind["shard_activation_pins"]
        _require(isinstance(pins, list) and bool(pins), f"{description} shard_activation_pins must be a nonempty array")

    pack_id = spec.get("pack_id")
    _require(isinstance(pack_id, str) and bool(pack_id), f"{description} pack_id must be nonempty")
    _require(model.get("pack_id") == pack_id, f"{description} pack_id does not match model identity")
    # Schema 8 is the first with version-independent compatibility; the pinned
    # producer's current schema is the newest it reads and writes.
    _require(type(model.get("schema_version")) is int
             and MIN_MODEL_SCHEMA_VERSION <= model["schema_version"] <= MAX_MODEL_SCHEMA_VERSION,
             f"{description} model schema_version must be {MIN_MODEL_SCHEMA_VERSION} through {MAX_MODEL_SCHEMA_VERSION}")

    artifact = spec.get("artifact")
    _require(isinstance(artifact, dict), f"{description} artifact must be an object")
    artifact_sha256 = artifact.get("sha256")
    _require(
        isinstance(artifact_sha256, str)
        and len(artifact_sha256) == SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in artifact_sha256),
        f"{description} artifact.sha256 must be a lowercase SHA-256 digest",
    )

    shards = model.get("shards")
    _require(isinstance(shards, list) and bool(shards), f"{description} model shards must be nonempty")
    shard_by_id: dict[str, dict[str, Any]] = {}
    for index, shard in enumerate(shards):
        _require(isinstance(shard, dict), f"{description} shard[{index}] must be an object")
        shard_id = shard.get("id")
        _require(isinstance(shard_id, str) and bool(shard_id), f"{description} shard[{index}].id must be nonempty")
        _require(shard_id not in shard_by_id, f"{description} contains duplicate shard id {shard_id!r}")
        shard_by_id[shard_id] = shard
        _normalize_selector_vector(shard.get("activation"), f"{description} shard {shard_id} activation")

    if not pins_present:
        global_activation = _normalize_selector_vector(
            spec.get("activation"), f"{description} activation"
        )
        for shard_id, shard in shard_by_id.items():
            shard_activation = _normalize_selector_vector(
                shard.get("activation"), f"{description} shard {shard_id} activation"
            )
            _require(
                global_activation == shard_activation,
                f"{description} global activation differs from shard {shard_id}",
            )
        return

    # Schema 2 pins are deliberately a complete shard-by-shard source map.
    # The legacy global selector remains well-formed metadata but no longer
    # substitutes for the narrower selectors on individual shards.
    _normalize_selector_vector(spec.get("activation"), f"{description} activation")
    seen: set[str] = set()
    for index, pin in enumerate(pins):
        _require(isinstance(pin, dict), f"{description} shard pin[{index}] must be an object")
        _require(
            set(pin) == {"shard_id", "activation"},
            f"{description} shard pin[{index}] must contain exactly shard_id and activation",
        )
        shard_id = pin["shard_id"]
        _require(isinstance(shard_id, str) and bool(shard_id), f"{description} pin[{index}].shard_id must be nonempty")
        _require(shard_id in shard_by_id, f"{description} pin references unknown shard {shard_id!r}")
        _require(shard_id not in seen, f"{description} contains duplicate pin for shard {shard_id!r}")
        seen.add(shard_id)
        pin_activation = _normalize_selector_vector(
            pin["activation"], f"{description} pin for shard {shard_id} activation"
        )
        shard_activation = _normalize_selector_vector(
            shard_by_id[shard_id]["activation"], f"{description} shard {shard_id} activation"
        )
        _require(
            pin_activation == shard_activation,
            f"{description} pin activation differs from shard {shard_id}",
        )
    _require(seen == set(shard_by_id), f"{description} shard pins are incomplete")


def _validate_spec_notice_assets(spec: Any, spec_path: Path, description: str) -> None:
    _require(isinstance(spec, dict), f"{description} spec must be an object")
    notices = spec.get("notices")
    _require(isinstance(notices, list) and bool(notices),
             f"{description} notices must name at least one asset")
    seen_notices: set[str] = set()
    for index, notice in enumerate(notices):
        field = f"{description} notices[{index}]"
        _require(isinstance(notice, str) and bool(notice), f"{field} must be a nonempty path")
        _require(notice not in seen_notices, f"{field} duplicates a notice path")
        seen_notices.add(notice)
        relative = PurePosixPath(notice)
        _require(not relative.is_absolute() and relative.as_posix() == notice
                 and "\\" not in notice and ":" not in notice and "\x00" not in notice
                 and all(part not in ("", ".", "..") for part in notice.split("/")),
                 f"{field} must be a safe normalized spec-relative path")

        current = spec_path.parent
        final_mode = None
        for part in relative.parts:
            current = current / part
            try:
                final_mode = current.lstat().st_mode
            except OSError as error:
                raise SourceInputError(f"{field} is missing or unreadable: {error}") from error
            _require(not stat.S_ISLNK(final_mode), f"{field} must not traverse a symlink")
        _require(final_mode is not None and stat.S_ISREG(final_mode),
                 f"{field} must resolve to a regular file")


def _spec_and_model(spec_activation: Any, shard_activations: list[Any], *,
                    schema_version: int = 1) -> tuple[dict[str, Any], dict[str, Any]]:
    shards = [
        {"id": f"fixture.shard.{index}", "activation": copy.deepcopy(activation)}
        for index, activation in enumerate(shard_activations)
    ]
    spec = {
        "schema_version": schema_version,
        "kind": {"artifact_kind": AUTHORED_KIND},
        "pack_id": "bifrost.fixture.authored",
        "artifact": {"sha256": "a" * SHA256_LENGTH},
        "activation": copy.deepcopy(spec_activation),
    }
    model = {"schema_version": 8, "pack_id": spec["pack_id"], "shards": shards}
    return spec, model


class AuthoredNativeGenerationInputTests(unittest.TestCase):
    def test_all_configured_authored_jobs_bind_source_identity_and_each_shard(self):
        config = _load_json("native-generation.json")
        self.assertIsInstance(config, dict)
        jobs = config.get("jobs")
        self.assertIsInstance(jobs, list)
        self.assertEqual(len(jobs), 48)
        shard_count = 0

        for job in jobs:
            with self.subTest(job=job.get("name")):
                self.assertEqual(set(job), {"name", "spec", "artifact"})
                spec_bytes = (ROOT / job["spec"]).read_bytes()
                model_bytes = (ROOT / job["artifact"]).read_bytes()
                spec = _load_json_bytes(spec_bytes, job["spec"])
                model = _load_json_bytes(model_bytes, job["artifact"])
                shard_count += len(model.get("shards", []))
                _validate_authored_model_source(spec, model, job["name"])
                self.assertEqual(spec["artifact"]["file_name"], Path(job["artifact"]).name)
                self.assertEqual(spec["artifact"]["sha256"], hashlib.sha256(model_bytes).hexdigest())
                self.assertEqual(spec["pack_version"], model["version"])
                for field in ("compatibility", "provenance", "license", "safety"):
                    self.assertEqual(spec[field], model[field], f"{job['name']} {field}")

        self.assertEqual(shard_count, 59)

    def test_jdk21_reviewed_obligations_are_selected_for_native_delivery(self):
        jobs = _load_json("native-generation.json")["jobs"]
        selected = [job for job in jobs if job["artifact"] ==
                    "semantic-packs/models/jdk21-result-use-obligations.json"]
        self.assertEqual(len(selected), 1)
        model = _load_json(selected[0]["artifact"])
        self.assertEqual(model["schema_version"], 8)
        self.assertNotIn("bifrost", model["compatibility"])
        self.assertEqual(model["shards"][0]["activation"], [{
            "toolchain": {"name": "jdk", "version": ">=21.0.0, <22.0.0"},
            "targets": ["jvm"],
        }])
        summaries = model["shards"][0]["payload"]["summaries"]
        self.assertEqual({summary["id"] for summary in summaries}, {
            "java.lang.string.trim.result-use",
            "java.nio.file.files.delete-if-exists.result-use",
        })
        status = next(summary for summary in summaries
                      if summary["id"] == "java.nio.file.files.delete-if-exists.result-use")
        self.assertEqual(status["completeness"], "partial")
        self.assertTrue(status["result_use_obligations"])

    def test_configured_direct_jobs_name_real_safe_spec_relative_notice_assets(self):
        config = _load_json("native-generation.json")
        jobs = config.get("jobs")
        self.assertIsInstance(jobs, list)
        for job in jobs:
            with self.subTest(job=job.get("name")):
                spec_path = ROOT / job["spec"]
                spec = _load_json_bytes(spec_path.read_bytes(), job["spec"])
                _validate_spec_notice_assets(spec, spec_path, job["name"])

    def test_notice_preflight_rejects_empty_unsafe_missing_nonfiles_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            pack_root = Path(directory) / "pack"
            notice_dir = pack_root / "notices"
            notice_dir.mkdir(parents=True)
            spec_path = pack_root / "model.spec.json"
            license_path = notice_dir / "LICENSE.txt"
            license_path.write_text("license fixture\n", encoding="utf-8")
            valid = {"notices": ["notices/LICENSE.txt"]}
            _validate_spec_notice_assets(valid, spec_path, "fixture")

            for notices, expected in [
                ([], "at least one asset"),
                (["/absolute/LICENSE.txt"], "safe normalized spec-relative path"),
                (["C:/outside/LICENSE.txt"], "safe normalized spec-relative path"),
                ([r"notices\LICENSE.txt"], "safe normalized spec-relative path"),
                (["../outside.txt"], "safe normalized spec-relative path"),
                (["./notices/LICENSE.txt"], "safe normalized spec-relative path"),
                (["notices/missing.txt"], "missing or unreadable"),
                (["notices"], "regular file"),
                (["notices/LICENSE.txt", "notices/LICENSE.txt"], "duplicates a notice path"),
            ]:
                with self.subTest(notices=notices):
                    with self.assertRaisesRegex(SourceInputError, expected):
                        _validate_spec_notice_assets({"notices": notices}, spec_path, "fixture")

            symlink_path = notice_dir / "linked-LICENSE.txt"
            symlink_path.symlink_to(license_path)
            with self.assertRaisesRegex(SourceInputError, "must not traverse a symlink"):
                _validate_spec_notice_assets({"notices": ["notices/linked-LICENSE.txt"]},
                                             spec_path, "fixture")

    def test_duplicate_json_keys_are_rejected_by_the_shared_runner_reader(self):
        with self.assertRaisesRegex(SourceInputError, "duplicate JSON key"):
            _load_json_bytes(b'{"schema_version": 1, "schema_version": 2}', "duplicate fixture")

    def test_legacy_selector_defaults_match_ruby_empty_shard_encoding(self):
        spec, model = _spec_and_model([{}], [[{}]])
        _validate_authored_model_source(spec, model, "ruby defaults")

        explicit_empty = {
            "package": None,
            "module": None,
            "toolchain": None,
            "artifact_sha256": None,
            "targets": [],
            "configurations": [],
        }
        spec, model = _spec_and_model([explicit_empty], [[explicit_empty]])
        _validate_authored_model_source(spec, model, "explicit empty defaults")

    def test_name_selector_optional_version_defaults_match_null(self):
        omitted = [{"package": {"name": "pkg:generic/nodejs.org/node"}, "targets": []}]
        explicit_null = [{"package": {"name": "pkg:generic/nodejs.org/node", "version": None}, "targets": []}]
        spec, model = _spec_and_model(omitted, [explicit_null])
        _validate_authored_model_source(spec, model, "optional name selector version")

        missing_name = [{"package": {"version": "=1.2.3"}, "targets": []}]
        spec, model = _spec_and_model(missing_name, [missing_name])
        with self.assertRaisesRegex(SourceInputError, "package.name must be nonempty"):
            _validate_authored_model_source(spec, model, "missing selector name")

    def test_legacy_global_selector_must_equal_every_shard(self):
        broad = [{"toolchain": {"name": "cpython", "version": ">=3.10, <3.15"}, "targets": []}]
        narrow = [{"toolchain": {"name": "cpython", "version": ">=3.12, <3.13"}, "targets": []}]
        for schema_version in (1, 2):
            spec, model = _spec_and_model(broad, [broad, narrow], schema_version=schema_version)
            with self.subTest(schema_version=schema_version):
                with self.assertRaisesRegex(SourceInputError, "global activation differs"):
                    _validate_authored_model_source(spec, model, "legacy heterogeneous")

    def test_schema_two_complete_pins_allow_narrowed_per_shard_selectors(self):
        broad = [{"package": {"name": "typescript", "version": "=7.0.2"},
                  "targets": [], "configurations": ["ES5", "ES2019"]}]
        narrow = [{"package": {"name": "typescript", "version": "=7.0.2"},
                   "targets": [], "configurations": ["ES2019"]}]
        pins = [
            {"shard_id": "fixture.shard.0", "activation": broad},
            {"shard_id": "fixture.shard.1", "activation": narrow},
        ]
        spec, model = _spec_and_model(broad, [broad, narrow], schema_version=2)
        spec["kind"]["shard_activation_pins"] = copy.deepcopy(pins)
        _validate_authored_model_source(spec, model, "schema two pins")

    def test_pins_reject_missing_extra_duplicate_null_and_empty_rows(self):
        broad = [{"targets": []}]
        narrow = [{"configurations": ["release"]}]
        valid = [
            {"shard_id": "fixture.shard.0", "activation": broad},
            {"shard_id": "fixture.shard.1", "activation": narrow},
        ]

        mutations = [
            (valid[:1], "incomplete"),
            (valid + [{"shard_id": "unknown", "activation": broad}], "unknown shard"),
            ([valid[0], valid[0]], "duplicate pin"),
            (None, "nonempty array"),
            ([], "nonempty array"),
            ([{"shard_id": "", "activation": broad}, valid[1]], "must be nonempty"),
            ([{"shard_id": "fixture.shard.0", "activation": None}, valid[1]], "nonempty array"),
        ]
        for pins, expected in mutations:
            with self.subTest(pins=pins):
                spec, model = _spec_and_model(broad, [broad, narrow], schema_version=2)
                spec["kind"]["shard_activation_pins"] = copy.deepcopy(pins)
                with self.assertRaisesRegex(SourceInputError, expected):
                    _validate_authored_model_source(spec, model, "mutated pins")

    def test_pin_kind_schema_and_authored_identity_are_closed(self):
        broad = [{"targets": []}]
        pins = [{"shard_id": "fixture.shard.0", "activation": broad}]
        spec, model = _spec_and_model(broad, [broad], schema_version=2)
        spec["kind"]["shard_activation_pins"] = copy.deepcopy(pins)

        mutated = copy.deepcopy(spec)
        mutated["kind"]["unexpected"] = True
        with self.assertRaisesRegex(SourceInputError, "kind contains unknown"):
            _validate_authored_model_source(mutated, model, "unknown kind field")

        mutated = copy.deepcopy(spec)
        mutated["kind"]["shard_activation_pins"][0]["unexpected"] = True
        with self.assertRaisesRegex(SourceInputError, "exactly shard_id and activation"):
            _validate_authored_model_source(mutated, model, "unknown pin field")

        mutated = copy.deepcopy(spec)
        mutated["schema_version"] = 1
        with self.assertRaisesRegex(SourceInputError, "require schema_version 2"):
            _validate_authored_model_source(mutated, model, "pins in schema one")

        mutated = copy.deepcopy(spec)
        mutated["kind"]["artifact_kind"] = "other"
        with self.assertRaisesRegex(SourceInputError, "not an authored semantic model"):
            _validate_authored_model_source(mutated, model, "wrong authored kind")

        wrong_model = copy.deepcopy(model)
        wrong_model["pack_id"] = "bifrost.other.model"
        with self.assertRaisesRegex(SourceInputError, "pack_id does not match"):
            _validate_authored_model_source(spec, wrong_model, "wrong model identity")

    def test_model_schema_stays_within_the_version_independent_range(self):
        broad = [{"targets": []}]
        spec, model = _spec_and_model(broad, [broad])
        for schema_version in (MIN_MODEL_SCHEMA_VERSION, 14, MAX_MODEL_SCHEMA_VERSION):
            with self.subTest(schema_version=schema_version):
                model["schema_version"] = schema_version
                _validate_authored_model_source(spec, model, "supported model schema")
        for schema_version in (MIN_MODEL_SCHEMA_VERSION - 1, MAX_MODEL_SCHEMA_VERSION + 1, "14"):
            with self.subTest(schema_version=schema_version):
                model["schema_version"] = schema_version
                with self.assertRaisesRegex(SourceInputError, "model schema_version must be"):
                    _validate_authored_model_source(spec, model, "unsupported model schema")

    def test_duplicate_authored_shard_ids_are_rejected(self):
        activation = [{"targets": []}]
        spec, model = _spec_and_model(activation, [activation, activation])
        model["shards"][1]["id"] = model["shards"][0]["id"]
        with self.assertRaisesRegex(SourceInputError, "duplicate shard id"):
            _validate_authored_model_source(spec, model, "duplicate authored shard")

    def test_unknown_or_changed_selector_fields_are_rejected_without_normalizing(self):
        spec_selector = [{"toolchain": {"name": "cpython", "version": "3.12"},
                          "targets": ["linux-x86_64"]}]
        model_selector = [{"toolchain": {"name": "cpython", "version": "3.12"},
                           "targets": ["linux-aarch64"]}]
        spec, model = _spec_and_model(spec_selector, [model_selector])
        with self.assertRaisesRegex(SourceInputError, "global activation differs"):
            _validate_authored_model_source(spec, model, "changed coordinate")

        for field in ("configuration", "artifact_id"):
            mutated = copy.deepcopy(model_selector)
            mutated[0][field] = "unexpected"
            spec, model = _spec_and_model(mutated, [mutated])
            with self.subTest(field=field):
                with self.assertRaisesRegex(SourceInputError, "unknown selector fields"):
                    _validate_authored_model_source(spec, model, "unknown selector")

        changed_artifact = [{"artifact_sha256": "b" * SHA256_LENGTH, "targets": []}]
        pinned_artifact = [{"artifact_sha256": "c" * SHA256_LENGTH, "targets": []}]
        spec, model = _spec_and_model(changed_artifact, [pinned_artifact])
        with self.assertRaisesRegex(SourceInputError, "global activation differs"):
            _validate_authored_model_source(spec, model, "changed artifact coordinate")

        spec_config = [{"configurations": ["ES5", "ES2019"], "targets": []}]
        shard_config = [{"configurations": ["ES2019", "ES5"], "targets": []}]
        spec, model = _spec_and_model(spec_config, [shard_config])
        with self.assertRaisesRegex(SourceInputError, "global activation differs"):
            _validate_authored_model_source(spec, model, "reordered configuration coordinates")

    def test_source_preflight_runs_before_identity_verification_action(self):
        workflow = (ROOT / ".github/workflows/content.yml").read_text(encoding="utf-8")
        preflight = workflow.index("python3 -B tests/test_authored_native_generation_inputs.py")
        identity_action = workflow.index("uses: ./.github/actions/verify-policy-identities")
        self.assertLess(preflight, identity_action)


if __name__ == "__main__":
    unittest.main()
