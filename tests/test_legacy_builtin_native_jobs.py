"""Native jobs for the packs Bifrost still embeds as its legacy built-in registry.

Bifrost-dev#4438 retires the embedded registry once releases deliver the same
public packs. These checks pin which of those packs are native jobs. They do
not establish runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "ad82cdd4e2a21d463d0122ebaf006e5c2ccf87d7"
# The rule-only and runtime-value-only models were migrated in a later commit.
RULE_ONLY_SOURCE_COMMIT = "825d2bcb1de3aea097b1149ae13ece24d920898c"
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

# These carry only rules or runtime values. They need a producer with the rule
# and runtime-exposure measurement lookups (bifrost-dev#8324).
RULE_ONLY = {
    "bifrost.java.lombok",
    "bifrost.rust.getset",
    "bifrost.scala.case-class",
    "bifrost.python-process-inputs",
    "bifrost.node-runtime-values-javascript",
    "bifrost.node-runtime-values-typescript",
}
RULE_ONLY_LOOKUPS = {"rule", "runtime_exposure"}


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class LegacyBuiltinNativeJobTests(unittest.TestCase):
    """Pin the delivered built-in packs and the producer-blocked remainder."""

    def test_every_delivered_builtin_pack_is_a_version_independent_job(self):
        jobs = _load("native-generation.json")["jobs"][FIRST_JOB:]
        self.assertEqual(len(jobs), len(DELIVERED | RULE_ONLY))
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
                commit = RULE_ONLY_SOURCE_COMMIT if model["pack_id"] in RULE_ONLY else SOURCE_COMMIT
                if model["schema_version"] == 8:
                    self.assertEqual(
                        spec["artifact"]["url"],
                        f"https://github.com/BrokkAi/bifrost-packs/blob/{commit}/{job['artifact']}",
                    )
                self.assertTrue(spec["measurement_queries"])
                if model["pack_id"] in RULE_ONLY:
                    kinds = {query["kind"] for query in spec["measurement_queries"]}
                    self.assertLessEqual(kinds, RULE_ONLY_LOOKUPS)
        self.assertEqual(seen, DELIVERED | RULE_ONLY)


if __name__ == "__main__":
    unittest.main()
