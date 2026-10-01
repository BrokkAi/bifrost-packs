"""The hook must check committed inputs even when working files differ."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK_CHECK = Path(__file__).resolve().parents[1] / "check_rule_stats_staged.py"


class StagedStatsTests(unittest.TestCase):
    def test_partial_staging_uses_index_and_preserves_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "tools").mkdir()
            (repo / "tools/rule_stats.py").write_text(
                "from pathlib import Path\n"
                "raise SystemExit(0 if Path('README.md').read_text() == "
                "Path('rule.txt').read_text() else 1)\n",
                encoding="utf-8",
            )
            (repo / "README.md").write_text("staged\n", encoding="utf-8")
            (repo / "rule.txt").write_text("staged\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            index = subprocess.check_output(["git", "write-tree"], cwd=repo)
            (repo / "rule.txt").write_text("unstaged\n", encoding="utf-8")
            command = [sys.executable, "-B", str(HOOK_CHECK)]
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(subprocess.check_output(["git", "write-tree"], cwd=repo), index)

            # Stale staged docs fail even if the working README is already updated.
            subprocess.run(["git", "add", "rule.txt"], cwd=repo, check=True)
            (repo / "README.md").write_text("unstaged\n", encoding="utf-8")
            index = subprocess.check_output(["git", "write-tree"], cwd=repo)
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("regenerate", result.stderr)
            self.assertEqual(subprocess.check_output(["git", "write-tree"], cwd=repo), index)
            self.assertEqual((repo / "README.md").read_text(), "unstaged\n")


if __name__ == "__main__":
    unittest.main()
