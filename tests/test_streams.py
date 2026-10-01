import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "release-contract"))

import content
import discover
import release


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _write_locked_repo(root, files):
    root.mkdir(parents=True, exist_ok=True)
    for name, data in {
        "LICENSE": "license text\n",
        "NOTICE.md": "notice text\n",
        "README.md": "content fixture\n",
    }.items():
        (root / name).write_text(data, encoding="utf-8")

    entries = []
    for name, text in sorted(files.items()):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = text.encode("utf-8")
        path.write_bytes(raw)
        entries.append(
            {
                "path": name,
                "source_path": f"source/{name}",
                "sha256": _sha256(raw),
                "classification": "public",
                "license": "Apache-2.0",
            }
        )

    aggregate = "".join(
        f"{entry['sha256']}  {entry['path']}\n"
        for entry in sorted(entries, key=lambda entry: entry["path"])
    )
    lock = {
        "schema_version": 1,
        "content_version": "0.1.0",
        "source": {"repository": "BrokkAi/bifrost-dev", "revision": "a" * 40},
        "engine": {
            "first_default_version": "0.13.0",
            "qualification_revision": "b" * 40,
            "default_enabled": False,
            "qualified_versions": [],
        },
        "files": entries,
        "aggregate_sha256": _sha256(aggregate.encode("utf-8")),
    }
    (root / "content-lock.json").write_text(
        json.dumps(lock, indent=2) + "\n", encoding="utf-8"
    )
    return lock


class StreamBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.parent = Path(self.temporary_directory.name)
        self.root = self.parent / "source"
        self.lock = _write_locked_repo(
            self.root,
            {
                "rules/demo/policies/example.rqlp": "policy\n",
                "semantic-packs/demo/model.json": '{"pack_id":"demo"}\n',
            },
        )

    def test_component_bundles_are_deterministic_disjoint_and_self_verifying(self):
        expected = {
            "rules": "rules/demo/policies/example.rqlp",
            "packs": "semantic-packs/demo/model.json",
        }
        opposite = {
            "rules": "semantic-packs/",
            "packs": "rules/",
        }

        for component, selected_path in expected.items():
            with self.subTest(component=component):
                first = self.parent / f"{component}-one.tar.gz"
                second = self.parent / f"{component}-two.tar.gz"
                content.build_bundle(first, self.root, component=component)
                content.build_bundle(second, self.root, component=component)
                self.assertEqual(first.read_bytes(), second.read_bytes())

                extracted = self.parent / f"{component}-extracted"
                extracted.mkdir()
                with tarfile.open(first, "r:gz") as archive:
                    names = archive.getnames()
                    archive.extractall(extracted)

                self.assertIn(selected_path, names)
                self.assertFalse(any(name.startswith(opposite[component]) for name in names))
                extracted_lock = content.verify_content(extracted)
                self.assertEqual(
                    {entry["path"] for entry in extracted_lock["files"]},
                    {selected_path},
                )


class StreamManifestTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "source"
        self.lock = _write_locked_repo(
            self.root,
            {
                "rules/demo/manifest.json": json.dumps(
                    {"id": "bifrost.demo", "schema_version": 3, "policies": []}
                )
                + "\n",
                "semantic-packs/demo/model.json": json.dumps(
                    {
                        "pack_id": "bifrost.demo-model",
                        "producer": "fixture",
                        "shards": [],
                        "language": "rust",
                        "schema_version": 1,
                    }
                )
                + "\n",
            },
        )

    def test_public_contents_filters_to_the_requested_stream(self):
        rules = release.public_contents(self.root, self.lock, component="rules")
        packs = release.public_contents(self.root, self.lock, component="packs")

        self.assertEqual({row["kind"] for row in rules}, {"policy-pack"})
        self.assertTrue(all(row["path"].startswith("rules/") for row in rules))
        self.assertEqual({row["kind"] for row in packs}, {"semantic-model"})
        self.assertTrue(
            all(row["path"].startswith("semantic-packs/") for row in packs)
        )

    def test_stream_tags_and_legacy_tag(self):
        def manifest(pack_id):
            return {"pack": {"id": pack_id}, "release_version": "2.4.1"}

        self.assertEqual(
            release.expected_tag(manifest("bifrost.public.rules")),
            "rules/v2.4.1",
        )
        self.assertEqual(
            release.expected_tag(manifest("bifrost.public.packs")),
            "packs/v2.4.1",
        )
        self.assertEqual(
            release.expected_tag(manifest("bifrost.public")),
            "v2.4.1",
        )
        self.assertEqual(
            release.expected_tag(manifest("bifrost.premium.packs")),
            "packs/v2.4.1",
        )
        self.assertEqual(
            release.expected_tag(manifest("bifrost.premium")),
            "v2.4.1",
        )


class StreamDiscoveryTagTests(unittest.TestCase):
    def _enumerate(self, component, tag_name):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        archive = root / "source.tar.gz"
        archive.write_bytes(b"stream archive")
        config = {
            "pack_id": f"bifrost.public.{component}",
            "repository": "https://github.com/test/public",
            "visibility": "public",
            "release_version": "1.2.3",
            "artifact_role": "source",
        }
        manifest = release.make_manifest(config, "b" * 40, [], archive)
        row = {
            "tag_name": tag_name,
            "draft": False,
            "prerelease": False,
            "assets": [
                {"id": 1, "name": "pack-release.json"},
                {"id": 2, "name": archive.name},
            ],
        }

        def fake_gh(arguments):
            if "--paginate" in arguments:
                return json.dumps([[row]]).encode("utf-8")
            if "assets/1" in " ".join(arguments):
                return json.dumps(manifest).encode("utf-8")
            if "git/ref/tags/" in " ".join(arguments):
                return json.dumps(
                    {"object": {"type": "commit", "sha": "b" * 40}}
                ).encode("utf-8")
            raise AssertionError(arguments)

        with patch.object(discover, "gh", side_effect=fake_gh):
            return discover.enumerate_candidates("test/public", "public", root)

    def test_correct_stream_tag_is_discovered(self):
        for component in ("rules", "packs"):
            with self.subTest(component=component):
                paths, index = self._enumerate(component, f"{component}/v1.2.3")

                self.assertEqual(len(paths), 1)
                self.assertEqual(
                    index["manifests"][0]["tag"], f"{component}/v1.2.3"
                )

    def test_legacy_style_tag_is_rejected_for_stream_release(self):
        for component in ("rules", "packs"):
            with self.subTest(component=component):
                with self.assertRaises(release.ReleaseError) as caught:
                    self._enumerate(component, "v1.2.3")

                self.assertEqual(caught.exception.code, "invalid-manifest")

    def test_other_stream_tag_is_rejected(self):
        for component, wrong_component in (("rules", "packs"), ("packs", "rules")):
            with self.subTest(component=component, wrong_component=wrong_component):
                with self.assertRaises(release.ReleaseError) as caught:
                    self._enumerate(component, f"{wrong_component}/v1.2.3")

                self.assertEqual(caught.exception.code, "invalid-manifest")


if __name__ == "__main__":
    unittest.main()
