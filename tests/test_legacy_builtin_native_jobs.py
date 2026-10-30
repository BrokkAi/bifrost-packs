"""Native jobs for the packs Bifrost still embeds as its legacy built-in registry.

Bifrost-dev#4438 retires the embedded registry once releases deliver the same
public packs. These checks pin which of those packs are native jobs and which
remain blocked by the pinned producer. They do not establish runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "ad82cdd4e2a21d463d0122ebaf006e5c2ccf87d7"
FIRST_JOB = 12

# Embedded pack IDs delivered by these jobs; Go os and the JDK and Python str
# result-use packs were already native before this set.
DELIVERED = {
    "bifrost.go.concurrency",
    "bifrost.go.concurrency-declarations",
    "bifrost.go.stdlib.bytes-declarations",
    "bifrost.go.stdlib.crypto-x509",
    "bifrost.go.stdlib.crypto-x509-declarations",
    "bifrost.go.stdlib.encoding-pem",
    "bifrost.go.stdlib.encoding-pem-declarations",
    "bifrost.go.stdlib.errors",
    "bifrost.go.stdlib.errors-declarations",
    "bifrost.go.stdlib.log",
    "bifrost.go.stdlib.log-declarations",
    "bifrost.go.stdlib.net",
    "bifrost.go.stdlib.net-declarations",
    "bifrost.go.stdlib.net-http",
    "bifrost.go.stdlib.net-http-declarations",
    "bifrost.go.stdlib.net-url",
    "bifrost.go.stdlib.net-url-declarations",
    "bifrost.go.stdlib.path-filepath",
    "bifrost.go.stdlib.sync-atomic",
    "bifrost.go.stdlib.sync-atomic-declarations",
    "bifrost.go.stdlib.testing",
    "bifrost.go.testify.assert",
    "bifrost.go.testify.assert-declarations",
    "bifrost.go.testify.require",
    "bifrost.go.testify.require-declarations",
    "bifrost.node-buffer-javascript-declarations",
    "bifrost.node-buffer-typescript-declarations",
    "bifrost.node-child-process-javascript-declarations",
    "bifrost.node-child-process-javascript-summaries",
    "bifrost.node-child-process-typescript-declarations",
    "bifrost.node-child-process-typescript-summaries",
    "bifrost.python-os-command-declarations",
    "bifrost.python-os-command-summaries",
    "bifrost.python-security-sink-declarations",
    "bifrost.python-security-sink-summaries",
    "bifrost.python-stdlib-api-declarations",
}

# These carry only rules or runtime values. The pinned producer requires a
# type, member or procedure lookup that resolves records, so they stay source-only.
PRODUCER_BLOCKED = {
    "semantic-packs/models/scala-case-class.json",
    "semantic-packs/models/lombok-1.18.42.json",
    "semantic-packs/models/getset-0.1.7.json",
    "semantic-packs/python/process-inputs/bifrost.python-process-inputs.json",
    "semantic-packs/node/runtime-values/javascript/bifrost.node-runtime-values.json",
    "semantic-packs/node/runtime-values/typescript/bifrost.node-runtime-values.json",
}
LOOKUP_PAYLOADS = {"types", "members", "summaries"}


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class LegacyBuiltinNativeJobTests(unittest.TestCase):
    def test_every_delivered_builtin_pack_is_a_version_independent_job(self):
        jobs = _load("native-generation.json")["jobs"][FIRST_JOB:]
        self.assertEqual(len(jobs), len(DELIVERED))
        seen = set()
        for job in jobs:
            with self.subTest(job=job["name"]):
                spec = _load(job["spec"])
                model_bytes = (ROOT / job["artifact"]).read_bytes()
                model = json.loads(model_bytes)
                seen.add(model["pack_id"])
                self.assertEqual(spec["pack_id"], model["pack_id"])
                self.assertGreaterEqual(model["schema_version"], 8)
                self.assertNotIn("bifrost", model["compatibility"])
                self.assertEqual(spec["artifact"]["sha256"], hashlib.sha256(model_bytes).hexdigest())
                if model["schema_version"] == 8:
                    self.assertEqual(
                        spec["artifact"]["url"],
                        f"https://github.com/BrokkAi/bifrost-packs/blob/{SOURCE_COMMIT}/{job['artifact']}",
                    )
                self.assertTrue(spec["measurement_queries"])
        self.assertEqual(seen, DELIVERED)

    def test_blocked_packs_have_no_lookup_records_and_no_job(self):
        artifacts = {job["artifact"] for job in _load("native-generation.json")["jobs"]}
        for path in PRODUCER_BLOCKED:
            with self.subTest(path=path):
                self.assertNotIn(path, artifacts)
                payloads = {
                    key
                    for shard in _load(path)["shards"]
                    for key, value in shard["payload"].items()
                    if value
                }
                self.assertFalse(payloads & LOOKUP_PAYLOADS)


if __name__ == "__main__":
    unittest.main()
