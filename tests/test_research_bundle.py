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
