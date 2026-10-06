import hashlib
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.content import ContentError, build_bundle, check_engine, verify_content


def _aggregate(files):
    lines = [
        f"{entry['sha256']}  {entry['path']}\n"
        for entry in sorted(files, key=lambda entry: entry["path"])
    ]
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


class ContentToolTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "repo"
        self.root.mkdir()
        for name, contents in {
            "LICENSE": "license text\n",
            "NOTICE.md": "notice text\n",
            "README.md": "readme text\n",
            "licenses/upstream/THIRD-PARTY.txt": "upstream license text\n",
            "rules/example.rql": "rule\n",
            "semantic-packs/library.json": '{"name":"example"}\n',
            "fixtures/positive/sample.rs": "fn main() {}\n",
            "scripts/upstream/build.py": "print('build')\n",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")
        self.entries = []
        for name in (
            "rules/example.rql",
            "semantic-packs/library.json",
            "fixtures/positive/sample.rs",
            "scripts/upstream/build.py",
            "licenses/upstream/THIRD-PARTY.txt",
        ):
            content = (self.root / name).read_bytes()
            self.entries.append(
                {
                    "path": name,
                    "source_path": f"source/{name}",
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "classification": "public",
                    "license": "Apache-2.0",
                }
            )
        self.lock = {
            "schema_version": 1,
            "content_version": "0.1.0",
            "source": {"repository": "BrokkAi/bifrost-dev", "revision": "a" * 40},
            "engine": {
                "first_default_version": "0.13.0",
                "qualification_revision": "b" * 40,
                "default_enabled": False,
                "qualified_versions": [],
            },
            "files": self.entries,
        }
        self._write_lock()

    def _write_lock(self):
        self.lock["aggregate_sha256"] = _aggregate(self.lock["files"])
        (self.root / "content-lock.json").write_text(
            json.dumps(self.lock, indent=2) + "\n", encoding="utf-8"
        )

    def test_verify_accepts_exact_locked_tree(self):
        result = verify_content(self.root)
        self.assertEqual(len(result["files"]), 5)

    def test_mixed_source_revisions_survive_bundle_and_reject_ambiguous_pins(self):
        self.entries[0]["source_revision"] = "c" * 40
        self._write_lock()
        output = self.root.parent / "mixed-source.tar.gz"
        build_bundle(output, self.root)
        with tarfile.open(output, "r:gz") as archive:
            bundled = json.load(archive.extractfile("content-lock.json"))
        self.assertEqual(bundled["files"][0]["source_revision"], "c" * 40)
        self.assertEqual(bundled["source"]["revision"], "a" * 40)
        self.entries[0]["source_revision"] = "master"
        self._write_lock()
        with self.assertRaisesRegex(ContentError, "source_revision must be a full"):
            verify_content(self.root)

    def test_verify_rejects_tampered_file(self):
        (self.root / "rules/example.rql").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(ContentError, "SHA-256 mismatch"):
            verify_content(self.root)

    def test_verify_rejects_missing_file(self):
        (self.root / "rules/example.rql").unlink()
        with self.assertRaisesRegex(ContentError, "missing"):
            verify_content(self.root)

    def test_verify_rejects_unlisted_file(self):
        (self.root / "fixtures/negative.rs").write_text("fn harmless() {}\n", encoding="utf-8")
        with self.assertRaisesRegex(ContentError, "unlisted content"):
            verify_content(self.root)

    def test_verify_requires_every_license_text_to_be_locked(self):
        (self.root / "licenses/extra.txt").write_text("additional terms\n", encoding="utf-8")
        with self.assertRaisesRegex(ContentError, "unlisted content file.*licenses/extra.txt"):
            verify_content(self.root)

    def test_verify_rejects_unsafe_manifest_path(self):
        self.lock["files"][0]["path"] = "rules/../../outside.rql"
        self._write_lock()
        with self.assertRaisesRegex(ContentError, "unsafe files\[0\].path"):
            verify_content(self.root)

    def test_verify_rejects_symlink_in_content_tree(self):
        target = self.root / "fixtures/positive/sample.rs"
        alias = self.root / "rules/alias.rql"
        alias.symlink_to(target)
        with self.assertRaisesRegex(ContentError, "symlink"):
            verify_content(self.root)

    def test_bundle_is_deterministic_and_has_fixed_metadata(self):
        output_one = self.root.parent / "first.tar.gz"
        output_two = self.root.parent / "second.tar.gz"
        build_bundle(output_one, self.root)
        build_bundle(output_two, self.root)
        self.assertEqual(output_one.read_bytes(), output_two.read_bytes())
        with tarfile.open(output_one, "r:gz") as archive:
            members = archive.getmembers()
            names = {member.name for member in members}
            self.assertEqual(
                names,
                {
                    "LICENSE",
                    "NOTICE.md",
                    "README.md",
                    "content-lock.json",
                    "rules/example.rql",
                    "semantic-packs/library.json",
                    "fixtures/positive/sample.rs",
                    "scripts/upstream/build.py",
                    "licenses/upstream/THIRD-PARTY.txt",
                },
            )
            for member in members:
                self.assertEqual(member.mtime, 0)
                self.assertEqual(member.mode, 0o644)
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
                self.assertEqual(member.uname, "")
                self.assertEqual(member.gname, "")

    def test_check_requires_explicit_engine_qualification(self):
        with self.assertRaisesRegex(ContentError, "qualified_versions records: none"):
            check_engine("0.12.0", self.root)
        self.lock["engine"]["qualified_versions"] = ["9.8.7"]
        self._write_lock()
        self.assertEqual(check_engine("9.8.7", self.root)["engine"]["qualified_versions"], ["9.8.7"])
        with self.assertRaisesRegex(ContentError, "No qualification is claimed for 0.13.0"):
            check_engine("0.13.0", self.root)

    def test_bundle_includes_optional_validation_manifest_when_present(self):
        (self.root / "validation.json").write_text('{"result":"inconclusive"}\n', encoding="utf-8")
        output = self.root.parent / "with-validation.tar.gz"
        build_bundle(output, self.root)
        with tarfile.open(output, "r:gz") as archive:
            self.assertIn("validation.json", archive.getnames())


if __name__ == "__main__":
    unittest.main()
