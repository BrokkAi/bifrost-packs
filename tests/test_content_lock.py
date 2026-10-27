"""Repository-agnostic checks for the shared sharded content-lock module."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "release-contract"))

import content_lock  # noqa: E402
import release  # noqa: E402


LAYOUT = {"directory": "locks", "depths": {"": 1, "packs/": 2}}


class ContentLockTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("packs/a/model.json", "packs/a/notes/n.txt", "packs/b.json", "notices/x.txt"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name + "\n")
        self.paths = {"packs/a/model.json", "packs/a/notes/n.txt", "packs/b.json", "notices/x.txt"}
        entries = [
            {"path": path, "sha256": content_lock.sha256_file(self.root / path), "license": "LicenseRef-Test"}
            for path in sorted(self.paths)
        ]
        self.single = {"schema_version": 1, "files": entries, "aggregate_sha256": content_lock.aggregate_sha256(entries)}
        (self.root / "lock.json").write_bytes(content_lock.lock_bytes(self.single))

    def _update(self, new_entry=lambda path, digest: None):
        return content_lock.update_lock(
            self.root, "lock.json", content_paths=self.paths, new_entry=new_entry, default_layout=LAYOUT
        )

    def test_converts_with_a_caller_layout_and_joins_byte_identically(self):
        self._update()
        header = json.loads((self.root / "lock.json").read_text())
        self.assertEqual(header, {"schema_version": 1, "file_shards": LAYOUT})
        self.assertEqual(
            sorted(p.relative_to(self.root / "locks").as_posix() for p in (self.root / "locks").rglob("*.json")),
            ["notices.json", "packs.json", "packs/a.json"],
        )
        joined = content_lock.read_lock(self.root, "lock.json")
        self.assertEqual(content_lock.lock_bytes(joined), content_lock.lock_bytes(self.single))
        self.assertEqual(joined, self.single)

    def test_new_entries_come_from_the_caller(self):
        self._update()
        (self.root / "packs/c.json").write_text("c\n")
        self.paths.add("packs/c.json")
        changes = self._update()
        self.assertEqual(changes["unlisted"], ["packs/c.json"])
        changes = self._update(lambda path, digest: {"path": path, "sha256": digest, "license": "MIT"})
        self.assertEqual(changes["added"], ["packs/c.json"])
        files = {e["path"]: e for e in content_lock.read_lock(self.root, "lock.json")["files"]}
        self.assertEqual(files["packs/c.json"]["license"], "MIT")

    def test_release_contract_joins_a_sharded_content_lock(self):
        (self.root / "content-lock.json").write_bytes(content_lock.lock_bytes(self.single))
        content_lock.update_lock(
            self.root, "content-lock.json", content_paths=self.paths,
            new_entry=lambda path, digest: None, default_layout=LAYOUT,
        )
        lock, raw = release.load_content_lock(self.root)
        self.assertEqual(raw, content_lock.lock_bytes(self.single))
        self.assertEqual(lock["aggregate_sha256"], self.single["aggregate_sha256"])

    def test_rejects_invalid_layouts(self):
        for layout in ({"directory": "locks"}, {"directory": "../x", "depths": {"": 1}},
                       {"directory": "locks", "depths": {"packs": 1}}, {"directory": "locks", "depths": {"": 0}}):
            header = {"schema_version": 1, "file_shards": layout}
            with self.subTest(layout=layout), self.assertRaises(content_lock.LockError):
                content_lock.shard_layout(header)


if __name__ == "__main__":
    unittest.main()
