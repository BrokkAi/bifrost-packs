import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "release-contract"))
sys.path.insert(0, str(ROOT / "tests"))

import audit_tuple
import content
import release
import test_baseline_release


class TupleAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sequence = 0

    def _case_dir(self, name):
        self.sequence += 1
        directory = self.root / f"{name}-{self.sequence}"
        directory.mkdir()
        return directory

    def _native_tuple(self):
        fixture = test_baseline_release.BaselineNativeContentsTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        archive, _ = fixture._native_archive()
        contents = audit_tuple.native_release.native_contents(archive, generator_version="0.11.5")
        output = self._case_dir("native-release")
        target = output / "bifrost.public.packs-1.0.0-native.tar.gz"
        target.write_bytes(archive.read_bytes())
        config = dict(
            pack_id="bifrost.public.packs",
            repository="https://github.com/BrokkAi/bifrost-packs",
            visibility="public",
            release_version="1.0.0",
            artifact_role="native",
            provenance={"engine_version": "0.11.5", "source_commit": "a" * 40},
        )
        manifest = release.make_manifest(config, "b" * 40, contents, target)
        manifest["qualification"] = {
            "integrity": {"status": "verified", "evidence": ["test descriptor"]},
            "behavior": {"status": "qualified", "evidence": ["deliberately ignored by audit"]},
        }
        (output / "pack-release.json").write_text(json.dumps(manifest))
        artifact = manifest["artifacts"][0]
        (output / (artifact["name"] + ".sha256")).write_text(artifact["sha256"] + "  " + artifact["name"] + "\n")
        return output / "pack-release.json", target

    def _rules_tuple(self, reproduction_metadata=None):
        case = self._case_dir("rules-case")
        source = case / "rule-source"
        source.mkdir()
        metadata = {
            "LICENSE": "license\n",
            "NOTICE.md": "notice\n",
            "README.md": "readme\n",
        }
        files = {
            "rules/demo/manifest.json": json.dumps({
                "schema_version": 2,
                "id": "demo",
                "version": "1.0.0",
                "name": "Demo",
                "description": "Fixture",
                "policies": [{
                    "path": "policies/check.rqlp",
                    "id": "demo.check",
                    "authored_hash": "a" * 64,
                    "resolved_semantic_hash": "a" * 64,
                    "supported_languages": ["python"],
                    "required_capabilities": ["structural-match"],
                }],
            }, sort_keys=True) + "\n",
            "rules/demo/policies/check.rqlp": "(policy :id \"demo.check\")\n",
        }
        lock_files = []
        for path, text in files.items():
            data = text.encode()
            target = source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            lock_files.append({"path": path, "source_path": "upstream/" + path, "sha256": hashlib.sha256(data).hexdigest(), "classification": "public", "license": "Apache-2.0"})
        lock = {
            "schema_version": 1,
            "content_version": "1.0.0",
            "source": {"repository": "https://github.com/example/source", "revision": "c" * 40},
            "engine": {"first_default_version": "0.13.0", "qualification_revision": "c" * 40, "default_enabled": False, "qualified_versions": []},
            "files": lock_files,
        }
        lock["aggregate_sha256"] = hashlib.sha256("".join(f"{row['sha256']}  {row['path']}\n" for row in sorted(lock_files, key=lambda item: item["path"])).encode()).hexdigest()
        (source / "content-lock.json").write_text(json.dumps(lock))
        for name, text in metadata.items():
            (source / name).write_text(text)
        for name, text in (reproduction_metadata or {}).items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        root = case / "rules-release"
        root.mkdir()
        import content
        archive = root / "bifrost.public.rules-1.0.0-source.tar.gz"
        content.build_bundle(archive, source, "rules")
        staged = root / "staged"
        staged.mkdir()
        import tarfile
        with tarfile.open(archive) as bundle:
            bundle.extractall(staged)
        staged_lock = content.verify_content(staged)
        contents = release.public_contents(staged, staged_lock, "rules")
        config = {"pack_id": "bifrost.public.rules", "repository": "https://github.com/BrokkAi/bifrost-packs", "visibility": "public", "release_version": "1.0.0", "artifact_role": "source"}
        manifest = release.make_manifest(config, "b" * 40, contents, archive, {
            "repository": staged_lock["source"]["repository"],
            "commit": staged_lock["source"]["revision"],
            "lock_sha256": "d" * 64,
        })
        manifest["qualification"] = {"integrity": {"status": "verified", "evidence": ["fixture"]}, "behavior": {"status": "pending", "evidence": []}}
        descriptor = root / "pack-release.json"
        descriptor.write_text(json.dumps(manifest))
        artifact = manifest["artifacts"][0]
        (root / (artifact["name"] + ".sha256")).write_text(artifact["sha256"] + "  " + artifact["name"] + "\n")
        return descriptor, archive

    def test_native_descriptor_and_shards_are_bound_and_behavior_stays_pending(self):
        manifest, _ = self._native_tuple()
        result = audit_tuple.audit_tuple(manifest)
        self.assertEqual(result["status"], "integrity_verified")
        self.assertEqual(result["descriptor_content_count"], 8)
        self.assertEqual(result["behavior"]["status"], "pending")
        self.assertEqual(result["descriptor_qualification"]["behavior"]["status"], "qualified")

    def test_rules_content_lock_classification_and_policy_descriptor_are_audited(self):
        manifest, _ = self._rules_tuple()
        result = audit_tuple.audit_tuple(manifest)
        self.assertEqual(result["policy_count"], 1)
        self.assertEqual(result["policy_identities"][0]["id"], "demo.check")
        self.assertEqual(result["public_content_lock"]["source_revision"], "c" * 40)
        self.assertEqual(result["public_content_lock"]["declared_source_lock_sha256"], "d" * 64)
        self.assertEqual(result["behavior"]["status"], "pending")

    def test_reproduction_metadata_is_audited_without_promoting_research_policies(self):
        manifest, _ = self._rules_tuple({
            'research/probe.rqlp': '(policy :id "research.only")\n',
            'research/fixtures/probe.java': 'class Probe {}\n',
            'docs/qualification.md': 'Behavior pending.\n',
            'release-contract/reproduce.py': '# reproduction helper\n',
        })
        result = audit_tuple.audit_tuple(manifest)
        self.assertEqual(result['policy_count'], 1)
        self.assertEqual([row['id'] for row in result['policy_identities']], ['demo.check'])

    def test_archive_tamper_and_descriptor_content_mismatch_fail_closed(self):
        manifest, archive = self._native_tuple()
        archive.write_bytes(archive.read_bytes() + b"tamper")
        with self.assertRaises(release.ReleaseError) as caught:
            audit_tuple.audit_tuple(manifest)
        self.assertEqual(caught.exception.code, "integrity-error")

        manifest, archive = self._native_tuple()
        data = json.loads(manifest.read_text())
        data["contents"][0]["completeness"] = "partial"
        manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(audit_tuple.AuditError, "descriptor content row differs"):
            audit_tuple.audit_tuple(manifest)

    def test_sidecar_and_extra_rules_files_are_rejected(self):
        manifest, archive = self._native_tuple()
        (manifest.parent / (archive.name + ".sha256")).write_text("0" * 64 + "  " + archive.name + "\n")
        with self.assertRaisesRegex(audit_tuple.AuditError, "sidecar differs"):
            audit_tuple.audit_tuple(manifest)

        manifest, archive = self._rules_tuple()
        import tarfile
        import io
        temp = archive.with_suffix(".tmp")
        with tarfile.open(archive) as source:
            entries = {member.name: source.extractfile(member).read() for member in source if member.isfile()}
        entries["rules/demo/policies/unindexed.rqlp"] = b"(policy)\n"
        with tarfile.open(temp, "w:gz") as output:
            for name, data in entries.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                output.addfile(info, io.BytesIO(data))
        archive.write_bytes(temp.read_bytes())
        data = json.loads(manifest.read_text())
        data["artifacts"][0]["sha256"] = release.digest(archive.read_bytes())
        data["artifacts"][0]["size_bytes"] = archive.stat().st_size
        manifest.write_text(json.dumps(data))
        (manifest.parent / (archive.name + ".sha256")).write_text(data["artifacts"][0]["sha256"] + "  " + archive.name + "\n")
        with self.assertRaisesRegex(content.ContentError, "unlisted content file"):
            audit_tuple.audit_tuple(manifest)

    def test_profile_rejections_are_typed_and_preserve_exact_profile_hash(self):
        manifest, _ = self._rules_tuple()
        profile = {
            "engine_version": "0.12.0",
            "build_identity": "fixture-build",
            "model_set_sha256": "e" * 64,
            "capability_contract_version": 1,
            "schemas": {key: [1, 2, 3, 4, 5, 6, 7] for key in release.SCHEMA_KEYS},
            "capabilities": [],
        }
        profile_path = self.root / "profile.json"
        profile_bytes = json.dumps(profile, sort_keys=True).encode()
        profile_path.write_bytes(profile_bytes)
        result = audit_tuple.audit_tuple(manifest, profile_path)
        self.assertEqual(result["status"], "integrity_verified")
        self.assertEqual(result["selection"]["status"], "rejected")
        self.assertEqual(result["selection"]["error"], "no-compatible-release")
        self.assertIn("structural-match", result["selection"]["message"])
        self.assertEqual(result["selection"]["engine_profile"]["profile"], profile)
        self.assertEqual(result["selection"]["engine_profile"]["sha256"], hashlib.sha256(profile_bytes).hexdigest())

        profile["capabilities"] = ["structural-match"]
        profile["schemas"]["policy_document"] = []
        profile_path.write_text(json.dumps(profile))
        result = audit_tuple.audit_tuple(manifest, profile_path)
        self.assertEqual(result["selection"]["status"], "rejected")
        self.assertEqual(result["selection"]["error"], "incompatible-schema")

    def test_missing_exact_dependency_is_reported_as_typed_selection_rejection(self):
        manifest, _ = self._rules_tuple()
        data = json.loads(manifest.read_text())
        data["release_dependencies"] = [{
            "pack_id": "bifrost.public.packs",
            "release_version": "0.2.0",
            "repository": "https://github.com/BrokkAi/bifrost-packs",
        }]
        manifest.write_text(json.dumps(data))
        profile = {
            "engine_version": "0.12.0",
            "build_identity": "fixture-build",
            "model_set_sha256": "e" * 64,
            "capability_contract_version": 1,
            "schemas": {key: [1, 2, 3, 4, 5, 6, 7] for key in release.SCHEMA_KEYS},
            "capabilities": ["structural-match"],
        }
        profile_path = self.root / "dependency-profile.json"
        profile_path.write_text(json.dumps(profile))
        result = audit_tuple.audit_tuple(manifest, profile_path, allow_unqualified=True)
        self.assertEqual(result["integrity"]["status"], "verified")
        self.assertEqual(result["selection"]["status"], "rejected")
        self.assertEqual(result["selection"]["error"], "no-compatible-release")
        self.assertTrue(result["selection"]["diagnostic"])
        self.assertTrue(result["selection"]["allow_unqualified"])

    def test_exact_dependency_selection_is_audited_without_promoting_behavior(self):
        manifest, _ = self._rules_tuple()
        dependency, _ = self._native_tuple()
        data = json.loads(manifest.read_text())
        data["release_dependencies"] = [{
            "pack_id": "bifrost.public.packs",
            "release_version": "1.0.0",
            "repository": "https://github.com/BrokkAi/bifrost-packs",
        }]
        manifest.write_text(json.dumps(data))
        profile = {
            "engine_version": "0.12.0", "build_identity": "fixture-build",
            "model_set_sha256": "e" * 64, "capability_contract_version": 1,
            "schemas": {key: [1, 2, 3, 4, 5, 6, 7] for key in release.SCHEMA_KEYS},
            "capabilities": ["structural-match"],
        }
        profile_path = self.root / "profile.json"
        profile_path.write_text(json.dumps(profile))
        result = audit_tuple.audit_tuple(manifest, profile_path, dependency_paths=[dependency])
        self.assertEqual(result["selection"]["status"], "selected")
        self.assertEqual(result["selection"]["receipt"]["dependencies"][0]["release_version"], "1.0.0")
        self.assertEqual(result["audited_dependencies"][0]["integrity"]["status"], "verified")
        self.assertEqual(result["behavior"]["status"], "pending")
        self.assertEqual(result["audited_dependencies"][0]["behavior"]["status"], "pending")

        descriptor = json.loads(dependency.read_text())
        descriptor["contents"][0]["completeness"] = "partial"
        dependency.write_text(json.dumps(descriptor))
        with self.assertRaisesRegex(audit_tuple.AuditError, "content row differs"):
            audit_tuple.audit_tuple(manifest, profile_path, dependency_paths=[dependency])

    def test_offline_missing_archive_is_rejected_without_fallback(self):
        manifest, archive = self._native_tuple()
        archive.unlink()
        with self.assertRaises(release.ReleaseError) as caught:
            audit_tuple.audit_tuple(manifest)
        self.assertEqual(caught.exception.code, "unavailable-credentials/network")

    def test_cli_output_cannot_overwrite_a_release_artifact(self):
        manifest, archive = self._native_tuple()
        before = archive.read_bytes()
        result = audit_tuple.main(["--manifest", str(manifest), "--output", str(archive)])
        self.assertEqual(result, release.ERROR_EXIT["integrity-error"])
        self.assertEqual(archive.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
