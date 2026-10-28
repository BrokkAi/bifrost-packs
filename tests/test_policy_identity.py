import hashlib
import json
from pathlib import Path
import os
import signal
import stat
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "release-contract"))

import release
from scripts.content import ContentError
import policy_identity
from policy_identity import (
    EVIDENCE_SCOPE,
    FIXED_ENVIRONMENT,
    MAX_CAPTURE_BYTES,
    PACK_ID,
    PolicyIdentityError,
    verify_policy_identities,
)

PRODUCTION_WORKSPACE_DIAGNOSTIC_CODES = frozenset(
    {
        "qualified-call-locator-zero",
        "qualified-call-locator-ambiguous",
        "qualified-call-locator-partial",
        "qualified-call-locator-inactive-model",
        "qualified-call-locator-incomplete",
        "qualified-receiver-locator-zero",
        "qualified-receiver-locator-ambiguous",
        "qualified-receiver-locator-partial",
        "qualified-receiver-locator-inactive-model",
        "qualified-receiver-locator-incomplete",
        "qualified-value-locator-zero",
        "qualified-value-locator-ambiguous",
        "qualified-value-locator-partial",
        "qualified-value-locator-inactive-model",
        "qualified-value-locator-incomplete",
        "endpoint-set-import-requires-workspace",
        "declaration-selection-import-requires-workspace",
        "catalogs-require-policy-run",
    }
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class PolicyIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "pack"
        self.root.mkdir()
        self.rules = self.root / "rules" / "fixture-pack"
        self.rules.mkdir(parents=True)
        self.output = self.base / "output"
        self.policy_data = {
            "available": b"(policy available)\n",
            "workspace": b"(policy workspace-required)\n",
        }
        self.authored = {
            "available": "a" * 64,
            "workspace": "b" * 64,
        }
        self.resolved = {"available": "c" * 64, "workspace": None}
        self._write_pack()
        self.binary = self._write_fake_binary()

    def tearDown(self):
        self.temporary.cleanup()

    def _write_pack(self, *, extra_policy=None, traversal=False, omit_resolved_hash=False):
        policies = []
        for name, data in self.policy_data.items():
            path = f"policies/{name}.rqlp"
            if traversal and name == "available":
                path = "../outside.rqlp"
            (self.rules / path).parent.mkdir(parents=True, exist_ok=True)
            if not traversal or name != "available":
                (self.rules / path).write_bytes(data)
            policy = {
                "path": path,
                "id": f"fixture.policy.{name}",
                "authored_hash": self.authored[name],
                "resolved_semantic_hash": self.resolved[name],
                "category": "correctness",
                "supported_languages": ["python", "rust"],
                "required_capabilities": ["structural-match"],
                "severity_rationale": "fixture",
                "remediation": "fixture",
            }
            if omit_resolved_hash and name == "available":
                del policy["resolved_semantic_hash"]
            policies.append(policy)
        if extra_policy:
            path, policy_id = extra_policy
            data = b"(policy duplicate identity)\n"
            (self.rules / path).parent.mkdir(parents=True, exist_ok=True)
            (self.rules / path).write_bytes(data)
            policies.append(
                {
                    "path": path,
                    "id": policy_id,
                    "authored_hash": "d" * 64,
                    "resolved_semantic_hash": "e" * 64,
                    "category": "correctness",
                    "supported_languages": ["python"],
                    "required_capabilities": ["structural-match"],
                    "severity_rationale": "fixture",
                    "remediation": "fixture",
                }
            )
        manifest = {
            "schema_version": 2,
            "id": "fixture.pack",
            "version": "1.0.0",
            "name": "Fixture pack",
            "description": "Fixture pack",
            "policies": policies,
        }
        manifest_bytes = json.dumps(manifest, sort_keys=True).encode() + b"\n"
        manifest_path = self.rules / "manifest.json"
        manifest_path.write_bytes(manifest_bytes)
        entries = []
        for path in sorted(self.root.glob("rules/fixture-pack/**/*.rqlp")):
            relative = path.relative_to(self.root).as_posix()
            entries.append(
                {
                    "path": relative,
                    "source_path": relative,
                    "sha256": sha256(path.read_bytes()),
                    "classification": "public",
                    "license": "Apache-2.0",
                }
            )
        entries.append(
            {
                "path": "rules/fixture-pack/manifest.json",
                "source_path": "rules/fixture-pack/manifest.json",
                "sha256": sha256(manifest_bytes),
                "classification": "public",
                "license": "Apache-2.0",
            }
        )
        lock = {
            "schema_version": 1,
            "content_version": "1.0.0",
            "source": {"repository": "https://example.invalid/fixture", "revision": "a" * 40},
            "engine": {
                "first_default_version": "0.12.0",
                "qualification_revision": "b" * 40,
                "default_enabled": False,
                "qualified_versions": [],
            },
            "files": entries,
        }
        lock["aggregate_sha256"] = sha256(
            "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in sorted(entries, key=lambda e: e["path"])).encode()
        )
        (self.root / "content-lock.json").write_text(json.dumps(lock, sort_keys=True) + "\n")

    def _write_fake_binary(self):
        config = self.base / "fake-config.json"
        config.write_text("{}\n")
        log = self.base / "invocations.jsonl"
        binary = self.base / "fake-bifrost"
        binary.write_text(
            "#!/usr/bin/env python3\n"
            "import hashlib, json, os, sys\n"
            "from pathlib import Path\n"
            "assert sys.argv[1] == 'policy-source-identity'\n"
            "source_id, policy_file = sys.argv[2:]\n"
            "config = json.loads(Path(os.environ['FAKE_CONFIG']).read_text())\n"
            "Path(os.environ['FAKE_LOG']).open('a').write(json.dumps({'argv': sys.argv[1:], 'env': {k: os.environ.get(k) for k in ['BIFROST_OPEN_PACKS_DISABLE', 'BIFROST_PARALLELISM', 'BIFROST_POLICY_PARALLELISM', 'RAYON_NUM_THREADS', 'JAVA_HOME']}}) + '\\n')\n"
            "entry = config[source_id]\n"
            "if 'raw_stdout' in entry:\n"
            "    sys.stdout.write(entry['raw_stdout'])\n"
            "else:\n"
            "    data = Path(policy_file).read_bytes()\n"
            "    report = {'format': 'bifrost_policy_source_identity/v1', 'source_id': source_id, 'policy_file': policy_file, 'source_sha256': hashlib.sha256(data).hexdigest(), 'authored_hash': entry['authored_hash'], 'resolved': entry['resolved'], 'provenance': {'source_sha256': 'raw-policy-file-bytes', 'authored_hash': 'PolicyRegistry::register_policy_bytes_deferred', 'resolved': 'PolicyRegistry::register_policy_bytes'}, 'engine_version': '0.13.0', 'build_identity': 'build-fixture'}\n"
            "    report.update(entry.get('overrides', {}))\n"
            "    sys.stdout.write(json.dumps(report))\n"
            "if entry.get('stderr'):\n"
            "    sys.stderr.write(entry['stderr'])\n"
            "sys.exit(entry.get('exit_code', 0))\n"
        )
        binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
        self.config = config
        self.log = log
        return binary

    def _configure_fake(self, *, overrides=None, exit_code=0):
        reports = {}
        for name in self.policy_data:
            source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/{name}.rqlp"
            reports[source_id] = {
                "authored_hash": self.authored[name],
                "resolved": (
                    {"status": "available", "semantic_hash": self.resolved[name]}
                    if self.resolved[name] is not None
                    else {
                        "status": "workspace-required",
                        "diagnostic_code": "qualified-value-locator-incomplete",
                        "message": "fixture requires a workspace model",
                    }
                ),
                "exit_code": exit_code,
            }
        for source_id, changes in (overrides or {}).items():
            reports[source_id].update(changes)
        self.config.write_text(json.dumps(reports, sort_keys=True) + "\n")
        os.environ["FAKE_CONFIG"] = str(self.config)
        os.environ["FAKE_LOG"] = str(self.log)

    def _verify(self):
        return verify_policy_identities(
            self.root,
            self.binary,
            self.output,
            "0.13.0",
            "build-fixture",
        )

    def test_success_enumerates_policies_and_retains_exact_process_evidence(self):
        self._configure_fake()
        result = self._verify()

        self.assertEqual(len(result["policies"]), 2)
        self.assertEqual(result["evidence_scope"], EVIDENCE_SCOPE)
        invocations = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(len(invocations), 2)
        for invocation in invocations:
            self.assertEqual(invocation["argv"][0], "policy-source-identity")
            self.assertEqual(invocation["env"], {key: FIXED_ENVIRONMENT[key] for key in (
                "BIFROST_OPEN_PACKS_DISABLE", "BIFROST_PARALLELISM",
                "BIFROST_POLICY_PARALLELISM", "RAYON_NUM_THREADS", "JAVA_HOME")})
        record_dir = self.output / "authoring-identities/public/bifrost.public.rules/fixture.policy.available"
        self.assertEqual(json.loads((record_dir / "process.json").read_text())["exit_code"], 0)
        self.assertEqual((record_dir / "stdout").read_bytes()[:1], b"{")
        self.assertTrue((record_dir / "stderr").is_file())
        self.assertEqual(json.loads((record_dir / "authoring-identity.json").read_text())["validation"], {
            "matches": True,
            "mismatch_reasons": [],
        })

    def test_workspace_required_requires_null_manifest_hash(self):
        self._configure_fake()
        result = self._verify()
        workspace = next(
            record for record in result["policies"] if record["source"]["policy_id"] == "fixture.policy.workspace"
        )
        self.assertEqual(workspace["report"]["actual"]["resolved"]["status"], "workspace-required")
        self.assertIsNone(workspace["source"]["expected_resolved_semantic_hash"])

    def test_workspace_required_accepts_complete_production_reason_catalog(self):
        self.assertEqual(
            policy_identity.SUPPORTED_WORKSPACE_DIAGNOSTIC_CODES,
            PRODUCTION_WORKSPACE_DIAGNOSTIC_CODES,
        )
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/workspace.rqlp"
        for reason in sorted(PRODUCTION_WORKSPACE_DIAGNOSTIC_CODES):
            with self.subTest(reason=reason):
                self._configure_fake(
                    overrides={
                        source_id: {
                            "resolved": {
                                "status": "workspace-required",
                                "diagnostic_code": reason,
                                "message": "fixture requires a workspace model",
                            }
                        }
                    }
                )
                result = self._verify()
                workspace = next(
                    record
                    for record in result["policies"]
                    if record["source"]["policy_id"] == "fixture.policy.workspace"
                )
                self.assertEqual(
                    workspace["report"]["actual"]["resolved"]["diagnostic_code"],
                    reason,
                )
                self.assertIsNone(workspace["source"]["expected_resolved_semantic_hash"])
                self.output = self.base / ("output-supported-reason-" + reason)

    def test_workspace_required_rejects_unsupported_tampered_reasons(self):
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/workspace.rqlp"
        for reason in ("budget-exhausted", "cancelled", "unknown-workspace-reason"):
            with self.subTest(reason=reason):
                self._configure_fake(
                    overrides={
                        source_id: {
                            "resolved": {
                                "status": "workspace-required",
                                "diagnostic_code": reason,
                                "message": "tampered workspace reason",
                            }
                        }
                    }
                )
                with self.assertRaisesRegex(
                    PolicyIdentityError, "not a supported workspace reason"
                ):
                    self._verify()
                record_dir = (
                    self.output
                    / "authoring-identities/public/bifrost.public.rules/fixture.policy.workspace"
                )
                observation = json.loads((record_dir / "authoring-identity.json").read_text())
                self.assertEqual(
                    observation["report"]["actual"]["resolved"]["diagnostic_code"],
                    reason,
                )
                self.assertFalse(observation["validation"]["matches"])
                self.output = self.base / ("output-unsupported-reason-" + reason)

    def test_cli_rejects_source_id_and_hash_mismatches(self):
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/available.rqlp"
        cases = (
            ("source_id", {"overrides": {"source_id": "wrong"}}),
            ("source_sha256", {"overrides": {"source_sha256": "f" * 64}}),
            ("authored_hash", {"overrides": {"authored_hash": "f" * 64}}),
            ("resolved_hash", {"overrides": {"resolved": {"status": "available", "semantic_hash": "f" * 64}}}),
        )
        for name, change in cases:
            with self.subTest(name=name):
                self._configure_fake(overrides={source_id: change})
                with self.assertRaises(PolicyIdentityError):
                    self._verify()
                process = self.output / "authoring-identities/public/bifrost.public.rules/fixture.policy.available/process.json"
                self.assertEqual(json.loads(process.read_text())["argv"][2], source_id)
                observation = json.loads((process.parent / "authoring-identity.json").read_text())
                raw_report = json.loads((process.parent / "stdout").read_text())
                self.assertEqual(observation["report"]["actual"], raw_report)
                self.assertIsNone(observation["report"]["parse_error"])
                self.assertFalse(observation["validation"]["matches"])
                self.output = self.base / ("output-" + name)

    def test_capture_process_timeout_kills_handwritten_child(self):
        child = self.base / "timeout-child"
        child.write_text(
            "#!/usr/bin/env python3\n"
            "import time\n"
            "time.sleep(60)\n"
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        started = time.monotonic()
        process = policy_identity._capture_process(
            [str(child)],
            cwd=self.base,
            env=os.environ.copy(),
            timeout_seconds=0.05,
        )

        self.assertTrue(process["invoked"])
        self.assertTrue(process["timed_out"])
        self.assertIsNone(process["spawn_error"])
        self.assertTrue(process["process_tree_cancellation_supported"])
        self.assertFalse(process["capture_incomplete"], process["capture_errors"])
        self.assertLess(time.monotonic() - started, 2.0)

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_capture_process_timeout_kills_descendant_holding_pipes(self):
        child = self.base / "descendant-pipe-child"
        child.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "import time\n"
            "if os.fork() == 0:\n"
            "    time.sleep(60)\n"
            "else:\n"
            "    os._exit(0)\n"
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        started = time.monotonic()
        process = policy_identity._capture_process(
            [str(child)],
            cwd=self.base,
            env=os.environ.copy(),
            timeout_seconds=0.05,
        )

        self.assertTrue(process["invoked"])
        self.assertTrue(process["timed_out"])
        self.assertTrue(process["process_tree_cancellation_supported"])
        self.assertFalse(process["capture_incomplete"], process["capture_errors"])
        self.assertLess(time.monotonic() - started, 2.0)

    @unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
    def test_capture_process_timeout_reports_escaped_setsid_descendant(self):
        child = self.base / "escaped-setsid-child"
        pid_file = self.base / "escaped-setsid.pid"
        child.write_text(
            "#!/usr/bin/env python3\n"
            "import os\n"
            "import sys\n"
            "import time\n"
            "from pathlib import Path\n"
            "pid_file = Path(sys.argv[1])\n"
            "if os.fork() == 0:\n"
            "    os.setsid()\n"
            "    pid_file.write_text(str(os.getpid()))\n"
            "    print('escaped', flush=True)\n"
            "    time.sleep(60)\n"
            "else:\n"
            "    while not pid_file.exists():\n"
            "        time.sleep(0.001)\n"
            "    os._exit(0)\n"
        )
        child.chmod(child.stat().st_mode | stat.S_IXUSR)
        escaped_pid = None
        started = time.monotonic()
        try:
            process = policy_identity._capture_process(
                [str(child), str(pid_file)],
                cwd=self.base,
                env=os.environ.copy(),
                timeout_seconds=0.5,
            )
            pid_deadline = time.monotonic() + 1.0
            while escaped_pid is None and time.monotonic() < pid_deadline:
                try:
                    escaped_pid = int(pid_file.read_text())
                except (FileNotFoundError, ValueError):
                    time.sleep(0.01)
            self.assertIsNotNone(escaped_pid)
            self.assertTrue(process["invoked"])
            self.assertTrue(process["timed_out"])
            self.assertTrue(process["process_tree_cancellation_supported"])
            self.assertTrue(process["capture_incomplete"], process["capture_errors"])
            self.assertIn("drain_timeout", process["capture_errors"])
            self.assertLess(time.monotonic() - started, 2.0)
        finally:
            if escaped_pid is None and pid_file.is_file():
                escaped_pid = int(pid_file.read_text())
            if escaped_pid is not None:
                try:
                    os.kill(escaped_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_cli_rejects_malformed_unexpected_and_duplicate_keys(self):
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/available.rqlp"
        malformed = {
            source_id: {
                "raw_stdout": '{"format":"bifrost_policy_source_identity/v1", "format":"duplicate"}'
            }
        }
        self._configure_fake(overrides=malformed)
        with self.assertRaisesRegex(PolicyIdentityError, "duplicate JSON key"):
            self._verify()

        self.output = self.base / "unexpected-output"
        self._configure_fake(overrides={source_id: {"overrides": {"unexpected": True}}})
        with self.assertRaisesRegex(PolicyIdentityError, "unexpected or missing keys"):
            self._verify()

    def test_bad_exit_and_missing_output_are_retained_and_rejected(self):
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/available.rqlp"
        self._configure_fake(overrides={source_id: {"exit_code": 7, "stderr": "bad exit\n"}})
        with self.assertRaisesRegex(PolicyIdentityError, "status 7"):
            self._verify()
        process = self.output / "authoring-identities/public/bifrost.public.rules/fixture.policy.available/process.json"
        self.assertEqual(json.loads(process.read_text())["exit_code"], 7)
        self.assertIn("bad exit\n", (process.parent / "stderr").read_text())

        self.output = self.base / "missing-output"
        self._configure_fake(overrides={source_id: {"raw_stdout": ""}})
        with self.assertRaises(PolicyIdentityError):
            self._verify()
        self.assertTrue((self.output / "authoring-identities/public/bifrost.public.rules/fixture.policy.available/stdout").is_file())

    def test_cli_output_is_bounded_and_retained(self):
        source_id = f"builtin:{PACK_ID}/rules/fixture-pack/policies/available.rqlp"
        self._configure_fake(overrides={source_id: {"raw_stdout": "x" * (MAX_CAPTURE_BYTES + 1)}})
        with self.assertRaisesRegex(PolicyIdentityError, "bounded capture"):
            self._verify()
        stdout = self.output / "authoring-identities/public/bifrost.public.rules/fixture.policy.available/stdout"
        self.assertEqual(stdout.stat().st_size, MAX_CAPTURE_BYTES)

    def test_inventory_rejects_duplicate_and_traversal_paths(self):
        self._configure_fake()
        self._write_pack(extra_policy=("policies/duplicate.rqlp", "fixture.policy.available"))
        with self.assertRaisesRegex(PolicyIdentityError, "duplicate policy identity"):
            self._verify()

        self.output = self.base / "traversal-output"
        self._write_pack(traversal=True)
        with self.assertRaises(release.ReleaseError):
            self._verify()

    def test_inventory_requires_explicit_resolved_hash_field(self):
        self._configure_fake()
        self._write_pack(omit_resolved_hash=True)
        with self.assertRaisesRegex(PolicyIdentityError, "missing resolved_semantic_hash"):
            self._verify()
        self.assertFalse(self.log.exists())

    def test_source_lock_mismatch_is_rejected_before_cli(self):
        self._configure_fake()
        path = self.rules / "policies/available.rqlp"
        path.write_bytes(b"changed bytes\n")
        with self.assertRaises(ContentError):
            self._verify()
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
