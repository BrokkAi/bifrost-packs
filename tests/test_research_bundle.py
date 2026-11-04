import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "release-contract"))

import release
from scripts import content


ROOT = Path(__file__).resolve().parents[1]


class ResearchBundleTests(unittest.TestCase):
    def test_source_archives_retain_rust_io_write_fixtures(self):
        fixture_root = "tests/cases/rust-io-write"
        expected = {
            f"{fixture_root}/{case}/{relative}"
            for case in ("positive", "near-miss")
            for relative in ("Cargo.toml", "src/lib.rs")
        }
        expected.add(f"{fixture_root}/README.md")
        for relative in sorted(expected):
            self.assertTrue((ROOT / relative).is_file(), relative)

        with tempfile.TemporaryDirectory() as directory:
            for component in (None, "rules", "packs"):
                with self.subTest(component=component):
                    archive_path = Path(directory) / f"{component or 'full'}-source.tar.gz"
                    content.build_bundle(archive_path, ROOT, component=component)
                    with tarfile.open(archive_path, "r:gz") as archive:
                        names = set(archive.getnames())
                        self.assertEqual(
                            {name for name in names if name.startswith(f"{fixture_root}/")},
                            expected,
                        )
                        for relative in sorted(expected):
                            self.assertEqual(
                                archive.extractfile(relative).read(),
                                (ROOT / relative).read_bytes(),
                            )
                        self.assertFalse(any(
                            name.startswith("tests/fixtures/semantic/rust-io-write/")
                            for name in names
                        ))

    def test_source_archive_retains_non_python_regression_fixtures(self):
        from test_content import ContentToolTests
        fixture = ContentToolTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        expected = {
            'tests/cases/recursion/positive/src/lib.rs': 'pub fn parse() {}\n',
            'tests/cases/recursion/positive/Cargo.toml': '[package]\nname="probe"\n',
            'tests/cases/recursion/positive/.bifrost/policies/probe.rqlp': '(policy)\n',
        }
        for relative, text in expected.items():
            path = fixture.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        archive_path = fixture.root.parent / 'fixture-source.tar.gz'
        content.build_bundle(archive_path, fixture.root, component='rules')
        with tarfile.open(archive_path) as archive:
            for relative, text in expected.items():
                self.assertEqual(archive.extractfile(relative).read(), text.encode())
            lock = json.load(archive.extractfile('content-lock.json'))
        self.assertFalse(any(entry['path'].startswith('tests/cases/') for entry in lock['files']))

    def test_tracked_research_is_carried_as_metadata_only(self):
        tracked = {
            item.decode("utf-8")
            for item in subprocess.check_output(
                ["git", "-C", str(ROOT), "ls-files", "-z", "--", "research"]
            ).split(b"\0")
            if item
        }
        self.assertTrue(tracked)
        self.assertFalse(any("__pycache__" in Path(path).parts for path in tracked))

        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "rules.tar.gz"
            content.build_bundle(archive_path, ROOT, component="rules")
            extracted = Path(directory) / "extracted"
            extracted.mkdir()
            with tarfile.open(archive_path, "r:gz") as archive:
                names = set(archive.getnames())
                archive.extractall(extracted)

            self.assertEqual(
                {name for name in names if name.startswith("research/")},
                tracked,
            )
            lock = content.verify_content(extracted)
            self.assertFalse(any(entry["path"].startswith("research/") for entry in lock["files"]))
            contents = release.public_contents(extracted, lock, component="rules")
            self.assertTrue(contents)
            self.assertTrue(all(item["kind"] in {"policy", "policy-pack"} for item in contents))
            self.assertFalse(any(item["path"].startswith("research/") for item in contents))


if __name__ == "__main__":
    unittest.main()
