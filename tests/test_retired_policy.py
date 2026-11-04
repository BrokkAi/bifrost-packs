"""Artifact/admission regression for the deliberately retired Go race policy."""
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "release-contract"))
sys.path.insert(0, str(ROOT / "scripts"))
import content
import release


class RetiredPolicyTests(unittest.TestCase):
    def test_rule_artifact_removes_retired_content_and_preserves_admission(self):
        # #79: keeping the retired policy while deleting its requirements would
        # falsely admit an artifact whose policy still needs Go race analysis.
        retired_id = "bifrost.correctness.go-data-race"
        retired_path = "rules/bifrost.code-smells/policies/go-data-race.rqlp"
        exclusive = {
            "normalized-concurrent-spawn",
            "concurrent-access-conflicts",
            "canonical-workspace-dispatch",
            "heap-location-identity",
            "reviewed-concurrency-models",
        }
        lock = content.verify_content(ROOT)
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            archive = directory / "rules.tar.gz"
            repeated = directory / "repeated.tar.gz"
            content.build_bundle(archive, ROOT, component="rules")
            content.build_bundle(repeated, ROOT, component="rules")
            self.assertEqual(archive.read_bytes(), repeated.read_bytes())
            rows = release.public_contents(ROOT, lock, component="rules")
            config = json.loads((ROOT / "release-config.rules.json").read_text())
            # This synthetic source pin identifies contract-test data only;
            # no profile or behavior claim about a real engine is fabricated.
            manifest = release.make_manifest(config, "a" * 40, rows, archive)
            manifest_path = directory / "pack-release.json"
            manifest_path.write_text(json.dumps(manifest))

            self.assertNotIn(retired_id, {row["identity"] for row in rows})
            self.assertNotIn(retired_path, {row["path"] for row in lock["files"]})
            required = set(manifest["compatibility"]["capabilities"]["required"])
            self.assertTrue(required.isdisjoint(exclusive))
            self.assertEqual(required, {name for row in rows for name in row["required_capabilities"]})
            self.assertIn("structural-match", required)
            self.assertIn("normalized-call", required)
            with tarfile.open(archive) as bundle:
                names = set(bundle.getnames())
                self.assertNotIn(retired_path, names)
                archived_lock = json.load(bundle.extractfile("content-lock.json"))
                self.assertNotIn(retired_path, {row["path"] for row in archived_lock["files"]})
                pack = json.load(bundle.extractfile("rules/bifrost.code-smells/manifest.json"))
                self.assertNotIn(retired_id, {row["id"] for row in pack["policies"]})
                for row in rows:
                    self.assertEqual(release.digest(bundle.extractfile(row["path"]).read()), row["sha256"])
            release.verify_artifact(manifest["artifacts"][0], archive)

            # Exercise actual capability admission without conflating it with
            # dependency resolution or a successful policy analysis. This
            # test-only profile is not an engine capability advertisement.
            profile = {
                "engine_version": "0.13.1",
                "build_identity": "test-only",
                "model_set_sha256": "b" * 64,
                "capability_contract_version": 1,
                "schemas": manifest["compatibility"]["schemas"],
                "capabilities": sorted(required),
            }
            release._eligible_candidates(
                [manifest_path], profile, config["pack_id"], "stable", None, None, True
            )
            self.assertEqual(manifest["qualification"]["behavior"]["status"], "pending")
            profile["capabilities"].remove("normalized-call")
            with self.assertRaisesRegex(release.ReleaseError, "normalized-call"):
                release._eligible_candidates(
                    [manifest_path], profile, config["pack_id"], "stable", None, None, True
                )


if __name__ == "__main__":
    unittest.main()
