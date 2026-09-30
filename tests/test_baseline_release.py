import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "release-contract"))

import release

_BUILD_RELEASE_SPEC = importlib.util.spec_from_file_location(
    "build_release", ROOT / "scripts" / "build-release.py"
)
build_release = importlib.util.module_from_spec(_BUILD_RELEASE_SPEC)
_BUILD_RELEASE_SPEC.loader.exec_module(build_release)


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _tar_bytes(files):
    import io

    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _deflate(data):
    compressor = zlib.compressobj(wbits=-15)
    return compressor.compress(data) + compressor.flush()


class BaselineRulesStageTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "root"
        self.root.mkdir()
        for name, text in {
            "LICENSE": "license\n",
            "NOTICE.md": "notice\n",
            "README.md": "readme\n",
            "content-lock.json": "{}\n",
        }.items():
            (self.root / name).write_text(text, encoding="utf-8")

        self.rule_bytes = {
            "crates/bifrost-policy/policy-packs/demo/manifest.json": b'{"id":"demo"}\n',
            "crates/bifrost-policy/policy-packs/demo/policies/check.rqlp": b"rule\n",
        }
        self.entries = [
            {
                "path": f"rules/{source_path.split('/policy-packs/', 1)[1]}",
                "source_path": source_path,
                "sha256": _sha256(data),
                "classification": "public",
                "license": "Apache-2.0",
            }
            for source_path, data in sorted(self.rule_bytes.items())
        ]
        self.baseline = {
            "repository": "https://github.com/BrokkAi/bifrost",
            "commit": "a" * 40,
            "tag": "v0.11.5",
            "rules": self.entries,
        }

    def _source_archive(self, overrides=None, omit=()):
        files = {
            f"bifrost-{self.baseline['tag']}/{path}": data
            for path, data in self.rule_bytes.items()
            if path not in omit
        }
        files.update(overrides or {})
        archive = self.root.parent / "source.tar.gz"
        archive.write_bytes(_tar_bytes(files))
        return archive

    def test_exact_rule_inventory_and_hash_are_accepted(self):
        archive = self._source_archive()
        stage = self.root.parent / "stage"
        stage.mkdir()

        lock = build_release.rules_stage(self.root, archive, self.baseline, stage)

        self.assertEqual(
            {entry["path"] for entry in lock["files"]},
            {entry["path"] for entry in self.entries},
        )
        for entry in self.entries:
            data = (stage / entry["path"]).read_bytes()
            self.assertEqual(_sha256(data), entry["sha256"])
        self.assertEqual(lock["source"]["revision"], self.baseline["commit"])

    def test_changed_rule_bytes_are_rejected(self):
        changed_path, _ = next(iter(self.rule_bytes.items()))
        archive = self._source_archive(
            {f"bifrost-{self.baseline['tag']}/{changed_path}": b"changed\n"}
        )
        stage = self.root.parent / "stage-changed"
        stage.mkdir()

        with self.assertRaises(release.ReleaseError) as caught:
            build_release.rules_stage(self.root, archive, self.baseline, stage)

        self.assertEqual(caught.exception.code, "integrity-error")

    def test_missing_rule_file_is_rejected(self):
        missing_path = next(iter(self.rule_bytes))
        archive = self._source_archive(omit=(missing_path,))
        stage = self.root.parent / "stage-missing"
        stage.mkdir()

        with self.assertRaises(release.ReleaseError) as caught:
            build_release.rules_stage(self.root, archive, self.baseline, stage)

        self.assertEqual(caught.exception.code, "integrity-error")


class BaselineNativeContentsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def _native_archive(self, *, identity_mismatch=False, raw_size_mismatch=False):
        prefix = "bifrost-semantic-packs/"
        files = {}
        authored_rows = []
        generated_rows = []
        definitions = [
            ("raw", b'{"items":[1]}\n', "raw"),
            ("deflate", b'{"items":[2]}\n', "deflate"),
            *[
                (f"authored-{number}", json.dumps({"items": [number]}).encode(), "raw")
                for number in range(3, 8)
            ],
            ("generated", b'{"items":[8]}\n', "raw"),
        ]

        for index, (name, raw_data, encoding) in enumerate(definitions):
            pack_id = f"demo.{name}"
            pack_version = "1.0.0"
            manifest_id = "wrong.identity" if identity_mismatch and index == 0 else pack_id
            manifest = {
                "pack_id": manifest_id,
                "version": pack_version,
                "language": "rust",
                "schema_version": 1,
                "completeness": "complete",
                "license": "Apache-2.0",
                "compatibility": {"engine": ">=0.11.5,<0.11.6"},
            }
            manifest_data = json.dumps(manifest, sort_keys=True).encode("utf-8")
            manifest_path = f"manifests/{name}.json"
            files[prefix + manifest_path] = manifest_data

            stored = raw_data if encoding == "raw" else _deflate(raw_data)
            shard_path = f"shards/{name}.json"
            files[prefix + shard_path] = stored
            declared_raw_size = len(raw_data) + 1 if raw_size_mismatch and index == 0 else len(raw_data)
            row = {
                    "pack_id": pack_id,
                    "pack_version": pack_version,
                    "language": "rust",
                    "manifest": {
                        "path": manifest_path,
                        "sha256": _sha256(manifest_data),
                        "bytes": len(manifest_data),
                    },
                    "shards": [
                        {
                            "encoding": encoding,
                            "raw_bytes": declared_raw_size,
                            "asset": {
                                "path": shard_path,
                                "sha256": _sha256(stored),
                                "bytes": len(stored),
                            },
                        }
                    ],
                }
            (generated_rows if name == "generated" else authored_rows).append(row)

        index = {
            "schema_version": 3,
            "generator": {"version": "0.11.5"},
            "packs": authored_rows,
            "generated_productions": generated_rows,
        }
        files[prefix + "index.json"] = json.dumps(index, sort_keys=True).encode("utf-8")
        files[prefix + "measurements.json"] = b'{"source":"fixture"}\n'
        checksum_lines = []
        for path, data in sorted(files.items()):
            if path == prefix + "measurements.json":
                continue
            relative = path.removeprefix(prefix)
            checksum_lines.append(f"{_sha256(data)}  {relative}\n")
        files[prefix + "SHA256SUMS"] = "".join(checksum_lines).encode("utf-8")

        archive = self.root / "native.tar.gz"
        archive.write_bytes(_tar_bytes(files))
        baseline = {"native_sha256": _sha256(archive.read_bytes()), "tag": "v0.11.5"}
        return archive, baseline

    def test_native_index_manifest_and_raw_and_deflate_shards_are_accepted(self):
        archive, baseline = self._native_archive()

        contents = build_release.native_contents(archive, baseline)

        self.assertEqual(len(contents), 8)
        self.assertEqual(
            {row["identity"] for row in contents},
            {"demo.raw", "demo.deflate", "demo.generated"}
            | {f"demo.authored-{number}" for number in range(3, 8)},
        )
        self.assertTrue(all(row["schemas"]["release_index"] == [3] for row in contents))

    def test_published_archive_checksum_mismatch_is_rejected(self):
        archive, baseline = self._native_archive()
        baseline["native_sha256"] = "0" * 64

        with self.assertRaises(release.ReleaseError) as caught:
            build_release.native_contents(archive, baseline)

        self.assertEqual(caught.exception.code, "integrity-error")

    def test_manifest_identity_mismatch_is_rejected(self):
        archive, baseline = self._native_archive(identity_mismatch=True)

        with self.assertRaises(release.ReleaseError) as caught:
            build_release.native_contents(archive, baseline)

        self.assertEqual(caught.exception.code, "integrity-error")

    def test_raw_shard_size_mismatch_is_rejected(self):
        archive, baseline = self._native_archive(raw_size_mismatch=True)

        with self.assertRaises(release.ReleaseError) as caught:
            build_release.native_contents(archive, baseline)

        self.assertEqual(caught.exception.code, "integrity-error")


def _profile():
    return {
        "engine_version": "0.11.5",
        "build_identity": "test-build-identity",
        "model_set_sha256": "a" * 64,
        "capability_contract_version": 1,
        "schemas": {key: [1, 2, 3, 4, 5, 6, 7] for key in release.SCHEMA_KEYS},
        "capabilities": ["structural-match"],
    }


class ReleaseDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.repository = "https://github.com/test/public"
        self.common_config = {
            "repository": self.repository,
            "visibility": "public",
            "engine_min_inclusive": "0.11.0",
            "engine_max_exclusive": "0.12.0",
        }
        self.paths = []

    def _candidate(
        self,
        pack_id,
        version,
        *,
        dependencies=(),
        minimum="0.11.0",
    ):
        directory = self.root / f"{pack_id.replace('.', '-')}-{version}"
        directory.mkdir()
        archive = directory / f"{pack_id}-{version}.tar.gz"
        archive.write_bytes(f"artifact {pack_id} {version}".encode("utf-8"))
        config = dict(
            self.common_config,
            pack_id=pack_id,
            release_version=version,
            engine_min_inclusive=minimum,
            artifact_role="native" if pack_id.endswith(".packs") else "policy",
        )
        manifest = release.make_manifest(config, "b" * 40, [], archive)
        manifest["qualification"] = {"status": "qualified", "evidence": ["fixture"]}
        if dependencies:
            manifest["release_dependencies"] = list(dependencies)
        path = directory / "pack-release.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.paths.append(path)
        return path, archive

    def _dependency(self, pack_id, version):
        return {
            "pack_id": pack_id,
            "release_version": version,
            "repository": self.repository,
        }

    def test_exact_pinned_dependency_wins_over_newer_stream_release(self):
        rule_path, _ = self._candidate(
            "bifrost.public.rules",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.packs", "1.0.0")],
        )
        pinned_pack_path, _ = self._candidate("bifrost.public.packs", "1.0.0")
        self._candidate("bifrost.public.packs", "2.0.0")

        resolved = release.resolve_release_set(
            self.paths, _profile(), "bifrost.public.rules"
        )
        receipt = release.select_release(
            self.paths, _profile(), "bifrost.public.rules"
        )

        self.assertEqual([item[2]["pack"]["id"] for item in resolved], [
            "bifrost.public.rules",
            "bifrost.public.packs",
        ])
        self.assertEqual(Path(resolved[1][1]), pinned_pack_path)
        self.assertEqual(receipt["release_version"], "1.0.0")
        self.assertEqual(receipt["dependencies"][0]["release_version"], "1.0.0")
        self.assertEqual(Path(resolved[0][1]), rule_path)

    def test_missing_dependency_fails(self):
        self._candidate(
            "bifrost.public.rules",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.packs", "1.0.0")],
        )

        with self.assertRaises(release.ReleaseError) as caught:
            release.resolve_release_set(
                self.paths, _profile(), "bifrost.public.rules"
            )

        self.assertEqual(caught.exception.code, "no-compatible-release")

    def test_incompatible_dependency_fails(self):
        self._candidate(
            "bifrost.public.rules",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.packs", "1.0.0")],
        )
        self._candidate("bifrost.public.packs", "1.0.0", minimum="0.11.6")

        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release(self.paths, _profile(), "bifrost.public.rules")

        self.assertEqual(caught.exception.code, "no-compatible-release")

    def test_dependency_cycle_fails(self):
        self._candidate(
            "bifrost.public.rules",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.packs", "1.0.0")],
        )
        self._candidate(
            "bifrost.public.packs",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.rules", "1.0.0")],
        )

        with self.assertRaises(release.ReleaseError) as caught:
            release.resolve_release_set(
                self.paths, _profile(), "bifrost.public.rules"
            )

        self.assertEqual(caught.exception.code, "invalid-manifest")

    def test_corrupt_dependency_artifact_fails(self):
        self._candidate(
            "bifrost.public.rules",
            "1.0.0",
            dependencies=[self._dependency("bifrost.public.packs", "1.0.0")],
        )
        _, pack_archive = self._candidate("bifrost.public.packs", "1.0.0")
        pack_archive.write_bytes(b"corrupt dependency artifact")

        with self.assertRaises(release.ReleaseError) as caught:
            release.select_release(self.paths, _profile(), "bifrost.public.rules")

        self.assertEqual(caught.exception.code, "integrity-error")


if __name__ == "__main__":
    unittest.main()
