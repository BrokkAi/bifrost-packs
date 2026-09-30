"""Focused contract tests for the shared native generation runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "native_generation", ROOT / "release-contract/native_generation.py"
)
native_generation = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(native_generation)


FAKE_TOOL = r'''#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

VERSION = __VERSION__
command, *args = sys.argv[1:]

def write_bundle(output, spec, artifact):
    output.mkdir(parents=True)
    spec_data = json.loads(Path(spec).read_text())
    data = Path(artifact).read_bytes()
    if os.environ.get("FAKE_NONDETERMINISTIC") and "/run-2/" in str(output):
        data += b"changed-on-second-run"
    (output / "payload.bin").write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    manifest = json.dumps({"id": spec_data["id"], "sha256": digest}, sort_keys=True).encode() + b"\n"
    (output / "manifest.json").write_bytes(manifest)
    row = {
        "pack_id": spec_data["id"],
        "pack_version": "1.0.0",
        "language": "fixture",
        "manifest": {"path": "manifest.json", "sha256": hashlib.sha256(manifest).hexdigest()},
        "shards": [],
    }
    index_version = os.environ.get("FAKE_INDEX_VERSION", VERSION)
    (output / "index.json").write_text(json.dumps({
        "schema_version": 3,
        "generator": {"version": index_version},
        "packs": [row],
        "generated_productions": [],
    }, sort_keys=True) + "\n")
    measurement = {"run_marker": os.urandom(8).hex(), "timing_ms": 1}
    (output / "measurements.json").write_text(json.dumps(measurement, sort_keys=True) + "\n")

if command == "generate":
    output, spec, artifact = args
    write_bundle(Path(output), spec, artifact)
elif command == "verify":
    if os.environ.get("FAKE_OMIT_PRODUCTIONS"):
        index_path = Path(args[0]) / "index.json"
        content = json.loads(index_path.read_text())
        content.pop("generated_productions", None)
        index_path.write_text(json.dumps(content, sort_keys=True) + "\n")
    bundle = Path(args[0])
    index = json.loads((bundle / "index.json").read_text())
    if index["schema_version"] != 3 or not (bundle / "measurements.json").is_file():
        raise SystemExit(3)
elif command == "merge":
    output, *inputs = args
    output = Path(output)
    output.mkdir(parents=True)
    packs = []
    generated = []
    for number, input_root in enumerate(map(Path, inputs)):
        index = json.loads((input_root / "index.json").read_text())
        packs.extend(index["packs"])
        generated.extend(index.get("generated_productions", []))
        for name in ("manifest.json", "payload.bin"):
            target = f"{number}-{name}"
            shutil.copyfile(input_root / name, output / target)
            if name == "manifest.json":
                for pack in index["packs"]:
                    pack["manifest"]["path"] = target
    merged = {
        "schema_version": 3,
        "generator": {"version": VERSION},
        "packs": packs,
        "generated_productions": generated,
    }
    (output / "index.json").write_text(json.dumps(merged, sort_keys=True) + "\n")
    measurements = json.loads((Path(inputs[0]) / "measurements.json").read_text())
    (output / "measurements.json").write_text(json.dumps(measurements, sort_keys=True) + "\n")
else:
    raise SystemExit(f"unknown command {command}")
'''


class NativeGenerationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        (self.root / "inputs").mkdir()
        (self.root / "inputs/source.json").write_text('{"id":"fixture.pack"}\n')
        (self.root / "inputs/artifact.bin").write_bytes(b"native-input")
        self.output = self.base / "output"

    def tearDown(self):
        self.temporary.cleanup()

    def write_config(self, *, version="0.11.5", recipes=None, jobs=None, source_build=False):
        binary = self.root / "fake-native-tool"
        binary.write_text(FAKE_TOOL.replace("__VERSION__", repr(version)))
        binary.chmod(0o755)
        if jobs is None:
            jobs = [] if recipes else [
                {"name": "fixture", "spec": "inputs/source.json", "artifact": "inputs/artifact.bin"}
            ]
        config = {
            "schema_version": 1,
            "generator": {
                "version": version,
                "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "repository": "BrokkAi/bifrost-dev",
                "commit": "4ec4489e850b809c9cc7750e4c450c7560c45de0",
                "asset": "bifrost-semantic-pack-linux-x86_64",
                "asset_sha256": "76016ab" + "0" * 57,
            },
            "jobs": jobs,
            "recipes": recipes if recipes is not None else [],
        }
        if source_build:
            config["generator"].update({
                "commit": "62fc36c09ddb96746e716c1c3456a99957521d91",
                "binary_sha256": None,
                "asset": "source.tar.gz",
                "asset_sha256": "f493b9f994aaaf46525dd4e05c22e0cf95917245fea2d942f39125d633411c0b",
                "build": {
                    "rust_toolchain": "1.97.1",
                    "cargo_lock_sha256": "a41ee93d487631314353cba4ab8d20a6d2546d9469ff5aaad4b33d1889f15590",
                },
            })
        config_path = self.root / "native-generation.json"
        config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "commit.gpgsign", "false"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "fixture"], check=True)
        return binary, config_path

    def generate(self, binary, config_path, output=None, build_receipt=None):
        return native_generation.run(self.root, config_path, binary, output or self.output, build_receipt)

    def write_build_receipt(self, binary, config_path, **overrides):
        generator = json.loads(config_path.read_text())["generator"]
        attestation = {
            "schema_version": 1,
            "generator_commit": generator["commit"],
            "source_archive_sha256": generator["asset_sha256"],
            "cargo_lock_sha256": generator["build"]["cargo_lock_sha256"],
            "rust_toolchain": generator["build"]["rust_toolchain"],
            "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }
        attestation.update(overrides)
        path = self.base / "build-receipt.json"
        path.write_text(json.dumps(attestation))
        return path

    def test_success_writes_archive_receipt_and_both_original_measurements(self):
        binary, config = self.write_config()
        receipt = self.generate(binary, config)

        self.assertTrue((self.output / "native.tar.gz").is_file())
        self.assertTrue((self.output / "generation.json").is_file())
        self.assertTrue((self.output / "measurements/run-1.json").is_file())
        self.assertTrue((self.output / "measurements/run-2.json").is_file())
        self.assertEqual(receipt["source"]["commit"], subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True
        ).strip())
        self.assertEqual(receipt["config_sha256"], hashlib.sha256(config.read_bytes()).hexdigest())
        self.assertEqual(receipt["archive"]["sha256"], hashlib.sha256((self.output / "native.tar.gz").read_bytes()).hexdigest())
        self.assertEqual(receipt["reproducibility"]["status"], "byte-identical-native-content")
        self.assertEqual(receipt["qualification"]["status"], "pending")
        self.assertIsNone(receipt["generator_build"])
        measurements = receipt["reproducibility"]["measurement_records"]
        for row in measurements:
            self.assertEqual(row["sha256"], hashlib.sha256((self.output / row["path"]).read_bytes()).hexdigest())
        self.assertNotEqual(measurements[0]["sha256"], measurements[1]["sha256"])

    def test_native_index_may_omit_empty_generated_productions(self):
        binary, config_path = self.write_config()
        with mock.patch.dict(os.environ, {"FAKE_OMIT_PRODUCTIONS": "1"}):
            receipt = self.generate(binary, config_path)
        self.assertEqual(receipt['qualification']['status'], 'pending')

    def test_binary_checksum_mismatch_fails_closed(self):
        binary, config_path = self.write_config()
        config = json.loads(config_path.read_text())
        config["generator"]["binary_sha256"] = "0" * 64
        config_path.write_text(json.dumps(config))
        subprocess.run(["git", "-C", str(self.root), "add", "native-generation.json"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "wrong binary pin"], check=True)

        with self.assertRaisesRegex(native_generation.NativeGenerationError, "binary checksum mismatch"):
            self.generate(binary, config_path)
        self.assertFalse(self.output.exists())

    def test_merged_generator_version_must_match_pinned_config_version(self):
        binary, config_path = self.write_config(version="0.11.5")
        with mock.patch.dict(os.environ, {"FAKE_INDEX_VERSION": "0.12.0"}):
            with self.assertRaisesRegex(native_generation.NativeGenerationError, "generator version mismatch"):
                self.generate(binary, config_path)

    def test_native_content_change_between_runs_fails_reproducibility(self):
        binary, config_path = self.write_config()
        with mock.patch.dict(os.environ, {"FAKE_NONDETERMINISTIC": "1"}):
            with self.assertRaisesRegex(native_generation.NativeGenerationError, "not reproducible"):
                self.generate(binary, config_path)

    def test_recipe_failure_preserves_nonzero_status_and_stops(self):
        recipe = self.root / "scripts/failing-recipe.sh"
        recipe.parent.mkdir()
        recipe.write_text("#!/usr/bin/env bash\nexit 17\n")
        binary, config_path = self.write_config(recipes=[{"name": "broken", "script": "scripts/failing-recipe.sh"}])

        with self.assertRaisesRegex(native_generation.NativeGenerationError, "exit status 17"):
            self.generate(binary, config_path)

    def test_dirty_source_fails_before_generation(self):
        binary, config_path = self.write_config()
        (self.root / "uncommitted.txt").write_text("uncommitted\n")

        with self.assertRaisesRegex(native_generation.NativeGenerationError, "must be clean"):
            self.generate(binary, config_path)
        self.assertFalse(self.output.exists())

    def test_recipe_that_dirties_source_fails_after_generation(self):
        (self.root / "README.md").write_text("clean fixture\n")
        recipe = self.root / "scripts/dirties-source.sh"
        recipe.parent.mkdir()
        recipe.write_text(
            "#!/usr/bin/env bash\n"
            "set -e\n"
            '"$BIFROST_SEMANTIC_PACK_BIN" generate "$1" '
            '"$PWD/inputs/source.json" "$PWD/inputs/artifact.bin"\n'
            "printf dirty >> README.md\n"
        )
        binary, config_path = self.write_config(
            recipes=[{"name": "dirty", "script": "scripts/dirties-source.sh"}]
        )

        with self.assertRaisesRegex(native_generation.NativeGenerationError, "became dirty"):
            self.generate(binary, config_path)

    def test_generator_012_is_independent_of_consumer_013(self):
        binary, config_path = self.write_config(version="0.12.0")
        (self.root / "release-config.packs.json").write_text(json.dumps({"engine_version": "0.13.0"}))
        subprocess.run(["git", "-C", str(self.root), "add", "release-config.packs.json"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "consumer profile"], check=True)

        receipt = self.generate(binary, config_path)

        self.assertEqual(receipt["generator"]["version"], "0.12.0")
        self.assertEqual(receipt["qualification"]["status"], "pending")

    def test_source_build_requires_receipt_without_fallback(self):
        binary, config = self.write_config(version="0.12.0", source_build=True)
        with self.assertRaisesRegex(native_generation.NativeGenerationError, "requires --build-receipt"):
            self.generate(binary, config)
        self.assertFalse(self.output.exists())

    def test_source_build_rejects_wrong_source_archive(self):
        binary, config = self.write_config(version="0.12.0", source_build=True)
        attestation = self.write_build_receipt(binary, config, source_archive_sha256="0" * 64)
        with self.assertRaisesRegex(native_generation.NativeGenerationError, "source_archive_sha256 mismatch"):
            self.generate(binary, config, build_receipt=attestation)
        self.assertFalse(self.output.exists())

    def test_source_build_binds_each_build_pin_and_executable(self):
        binary, config = self.write_config(version="0.12.0", source_build=True)
        for field, value in (
            ("generator_commit", "0" * 40),
            ("cargo_lock_sha256", "0" * 64),
            ("rust_toolchain", "1.97.2"),
            ("binary_sha256", "0" * 64),
            ("schema_version", True),
        ):
            with self.subTest(field=field):
                attestation = self.write_build_receipt(binary, config, **{field: value})
                with self.assertRaises(native_generation.NativeGenerationError):
                    self.generate(binary, config, build_receipt=attestation)
        self.assertFalse(self.output.exists())

    def test_source_build_012_emits_exact_attestation_and_pending_receipt(self):
        binary, config = self.write_config(version="0.12.0", source_build=True)
        attestation = self.write_build_receipt(binary, config)
        receipt = self.generate(binary, config, build_receipt=attestation)
        self.assertEqual(receipt["generator_build"], json.loads(attestation.read_text()))
        self.assertEqual(receipt["binary_sha256"], hashlib.sha256(binary.read_bytes()).hexdigest())
        self.assertIsNone(receipt["generator"]["binary_sha256"])
        self.assertEqual(receipt["generator"]["version"], "0.12.0")
        self.assertEqual(receipt["qualification"]["status"], "pending")

    def test_prebuilt_rejects_build_receipt(self):
        binary, config = self.write_config()
        attestation = self.base / "unexpected-receipt.json"
        attestation.write_text("{}")
        with self.assertRaisesRegex(native_generation.NativeGenerationError, "prebuilt generator"):
            self.generate(binary, config, build_receipt=attestation)

    def test_build_config_requires_exact_fields_and_prebuilt_hash(self):
        binary, config_path = self.write_config()
        original = json.loads(config_path.read_text())
        invalid_generators = []
        no_hash = dict(original["generator"], binary_sha256=None)
        invalid_generators.append(no_hash)
        for build in (
            {"rust_toolchain": "1.97.1"},
            {"rust_toolchain": "stable", "cargo_lock_sha256": "a" * 64},
            {"rust_toolchain": "1.97.1", "cargo_lock_sha256": "not-a-hash"},
            {"rust_toolchain": "1.97.1", "cargo_lock_sha256": "a" * 64, "extra": True},
        ):
            invalid_generators.append(dict(no_hash, build=build))
        for generator in invalid_generators:
            with self.subTest(generator=generator):
                config = dict(original, generator=generator)
                config_path.write_text(json.dumps(config))
                with self.assertRaises(native_generation.NativeGenerationError):
                    native_generation._validate_config(self.root.resolve(), config_path)


if __name__ == "__main__":
    unittest.main()
