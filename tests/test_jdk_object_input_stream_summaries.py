"""Pin the reviewed ObjectInputStream constructor summary and its delivery.

These checks pin source content and the native job. Runtime behavior is
qualified by the java-objectinputstream-read-without-filter policy fixture.
"""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = "semantic-packs/jvm/object-input-stream/bifrost.jdk-object-input-stream-summaries.json"
SPEC = "semantic-packs/jvm/jdk-object-input-stream-summaries.spec.json"
FIXTURE = "fixtures/policy/bifrost.security/java-objectinputstream-read-without-filter"


class JdkObjectInputStreamSummariesTests(unittest.TestCase):
    def test_constructor_result_is_a_fresh_allocation_not_its_input(self):
        pack = json.loads((ROOT / PACK).read_text())
        self.assertNotIn("bifrost", pack["compatibility"])
        self.assertFalse(pack["safety"]["review_required"])
        self.assertEqual(len(pack["shards"]), 1)
        payload = pack["shards"][0]["payload"]
        self.assertEqual(payload["kind"], "procedure_summaries")
        [summary] = payload["summaries"]
        self.assertEqual(summary["target"], {
            "path": "java.base/java/io/ObjectInputStream.java",
            "symbol": "java.io.ObjectInputStream.<init>(java.io.InputStream)",
            "has_receiver": False,
            "parameter_count": 1,
        })
        self.assertEqual(summary["completeness"], "complete")
        self.assertEqual(summary["effects"], [{
            "kind": "allocation",
            "event": "java.io.objectinputstream.init.allocation",
            "output": {"kind": "normal_return"},
        }])
        # The input flows into the stream, but the stream is not the input.
        self.assertEqual(summary["transfers"], [{
            "input": {"kind": "parameter", "ordinal": 0},
            "exit_kind": "normal",
            "output": {"kind": "normal_return"},
            "value_transfer": {"kind": {"kind": "conversion", "preservation": "changing"},
                               "operation": {"kind": "none"}},
        }])
        # The constructor reads the stream header, which advances the input.
        self.assertNotIn("ordinary_heap_unchanged", summary)

    def test_native_job_pins_the_reviewed_source(self):
        spec = json.loads((ROOT / SPEC).read_text())
        source = (ROOT / PACK).read_bytes()
        pack = json.loads(source)
        self.assertEqual(spec["artifact"]["sha256"], hashlib.sha256(source).hexdigest())
        self.assertTrue(spec["artifact"]["url"].endswith("/" + PACK))
        self.assertEqual(spec["kind"], {"artifact_kind": "authored_semantic_model"})
        self.assertEqual(spec["activation"], pack["shards"][0]["activation"])
        jobs = json.loads((ROOT / "native-generation.json").read_text())["jobs"]
        self.assertEqual([job for job in jobs if job["name"] == "jdk-object-input-stream-summaries"],
                         [{"name": "jdk-object-input-stream-summaries", "spec": SPEC, "artifact": PACK}])

    def test_policy_fixture_workspaces_carry_the_released_bytes(self):
        source = (ROOT / PACK).read_bytes()
        for workspace in (FIXTURE, FIXTURE + "/incomplete"):
            with self.subTest(workspace=workspace):
                copy = ROOT / workspace / ".bifrost/semantic-models" / Path(PACK).name
                self.assertEqual(copy.read_bytes(), source)


if __name__ == "__main__":
    unittest.main()
