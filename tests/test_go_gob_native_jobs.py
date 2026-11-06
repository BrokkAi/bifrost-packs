"""Pin the encoding/gob native jobs and the net interface summaries (#192).

These checks pin source inputs only. Runtime behavior is recorded in
fixtures/policy/bifrost.security/go-gob-decode-network-input/README.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts.content import read_lock


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "3745e66f03f8599337aa2d72b58c43611414d37e"
# The gob summaries dropped Decode and DecodeValue in a later commit.
GOB_SUMMARIES_COMMIT = "9849718fe0945d4c77011b28616b8f3ad375ba05"
GOB_JOBS = {
    "go-stdlib-encoding-gob": {
        "spec": "semantic-packs/go/go-stdlib-encoding-gob.spec.json",
        "model": "semantic-packs/models/go-stdlib-encoding-gob.json",
        "pack_id": "bifrost.go.stdlib.encoding-gob",
        "completeness": "complete",
        "source_commit": GOB_SUMMARIES_COMMIT,
    },
    "go-stdlib-encoding-gob-declarations": {
        "spec": "semantic-packs/go/go-stdlib-encoding-gob-declarations.spec.json",
        "model": "semantic-packs/models/go-stdlib-encoding-gob-declarations.json",
        "pack_id": "bifrost.go.stdlib.encoding-gob-declarations",
        "completeness": "partial",
        "source_commit": SOURCE_COMMIT,
    },
}
NET_MODEL = "semantic-packs/models/go-stdlib-net.json"
INTERFACE_SUMMARIES = {
    "net.Conn.Close()",
    "net.Conn.LocalAddr()",
    "net.Conn.RemoteAddr()",
    "net.Conn.SetDeadline(t time.Time)",
    "net.Conn.SetReadDeadline(t time.Time)",
    "net.Conn.SetWriteDeadline(t time.Time)",
    "net.Listener.Accept()",
    "net.Listener.Close()",
    "net.Listener.Addr()",
}


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class GoGobNativeJobTests(unittest.TestCase):
    """Pin the gob jobs, the net interface summaries and the fixture copies."""

    def test_gob_jobs_are_adjacent_and_bind_their_specs(self):
        jobs = _load("native-generation.json")["jobs"]
        names = [job["name"] for job in jobs]
        start = names.index("go-stdlib-encoding-gob")
        self.assertEqual(names[start:start + 2], list(GOB_JOBS))
        for job in jobs[start:start + 2]:
            expected = GOB_JOBS[job["name"]]
            with self.subTest(job=job["name"]):
                self.assertEqual(job, {"name": job["name"], "spec": expected["spec"], "artifact": expected["model"]})
                spec = _load(expected["spec"])
                model_bytes = (ROOT / expected["model"]).read_bytes()
                model = json.loads(model_bytes)
                self.assertEqual(spec["pack_id"], expected["pack_id"])
                self.assertEqual(model["pack_id"], expected["pack_id"])
                self.assertEqual(spec["pack_version"], model["version"])
                self.assertEqual(model["schema_version"], 8)
                self.assertEqual(model["completeness"], expected["completeness"])
                self.assertEqual(model["license"], "BSD-3-Clause")
                self.assertEqual(spec["provenance"], {"source": "https://pkg.go.dev/encoding/gob", "revision": "go1.26.0"})
                self.assertEqual(spec["notices"], ["notices/go-1.26.0-BSD-3-Clause.txt"])
                self.assertEqual(spec["artifact"]["sha256"], _sha256(model_bytes))
                self.assertEqual(
                    spec["artifact"]["url"],
                    f"https://github.com/BrokkAi/bifrost-packs/blob/{expected['source_commit']}/{expected['model']}",
                )

    def test_decoder_methods_have_no_summary(self):
        # The schema can't express Decode's write into its argument, and a
        # complete summary with no transfers would claim it writes nothing.
        summaries = _load(GOB_JOBS["go-stdlib-encoding-gob"]["model"])["shards"][0]["payload"]["summaries"]
        symbols = {row["target"]["symbol"] for row in summaries}
        self.assertEqual(symbols, {
            "encoding/gob.NewDecoder(r io.Reader)",
            "encoding/gob.NewEncoder(w io.Writer)",
            "encoding/gob.Encoder.Encode(e any)",
            "encoding/gob.Encoder.EncodeValue(value reflect.Value)",
            "encoding/gob.Register(value any)",
            "encoding/gob.RegisterName(name string, value any)",
        })
        self.assertTrue(all(row["completeness"] == "complete" for row in summaries))

    def test_every_gob_callable_is_a_complete_family(self):
        payload = _load(GOB_JOBS["go-stdlib-encoding-gob-declarations"]["model"])["shards"][0]["payload"]
        names = {row["locator"]["symbol"] for row in payload["members"]}
        self.assertEqual(names, {
            "encoding/gob.NewDecoder",
            "encoding/gob.NewEncoder",
            "encoding/gob.Register",
            "encoding/gob.RegisterName",
            "encoding/gob.Decoder.Decode",
            "encoding/gob.Decoder.DecodeValue",
            "encoding/gob.Encoder.Encode",
            "encoding/gob.Encoder.EncodeValue",
        })
        for row in payload["members"]:
            with self.subTest(member=row["locator"]["symbol"]):
                self.assertTrue(row["callable_family_complete"])
                self.assertEqual(row.get("receiver"), {"pointer": True} if row["member_kind"] == "method" else None)

    def test_net_interface_summaries_claim_every_implementation(self):
        model = _load(NET_MODEL)
        self.assertEqual(model["version"], "3.0.0")
        summaries = model["shards"][0]["payload"]["summaries"]
        claimed = {row["target"]["symbol"] for row in summaries if row.get("covers_overrides")}
        self.assertEqual(claimed, INTERFACE_SUMMARIES)
        for row in summaries:
            if row["target"]["symbol"] in INTERFACE_SUMMARIES:
                with self.subTest(summary=row["id"]):
                    self.assertTrue(row["target"]["has_receiver"])
                    self.assertEqual(row["completeness"], "complete")
                    self.assertEqual(row["transfers"], [])
        spec = _load("semantic-packs/go/go-stdlib-net.spec.json")
        self.assertEqual(spec["pack_version"], "3.0.0")
        self.assertEqual(
            spec["artifact"]["url"],
            f"https://github.com/BrokkAi/bifrost-packs/blob/{SOURCE_COMMIT}/{NET_MODEL}",
        )

    def test_fixture_models_match_the_published_sources(self):
        fixture = ROOT / "fixtures/policy/bifrost.security/go-gob-decode-network-input"
        for workspace in (fixture, fixture / "incomplete"):
            for name in (
                "go-stdlib-net-declarations.json",
                "go-stdlib-net.json",
                "go-stdlib-encoding-gob-declarations.json",
                "go-stdlib-encoding-gob.json",
            ):
                with self.subTest(workspace=workspace.name, model=name):
                    self.assertEqual(
                        (workspace / ".bifrost/semantic-models" / name).read_bytes(),
                        (ROOT / "semantic-packs/models" / name).read_bytes(),
                    )
            self.assertEqual(
                (workspace / ".bifrost/policies/gob-decode-network-input.rqlp").read_bytes(),
                (ROOT / "rules/bifrost.security/policies/go/gob-decode-network-input.rqlp").read_bytes(),
            )

    def test_new_specs_and_models_are_locked_public_bsd(self):
        entries = {row["path"]: row for row in read_lock(ROOT)["files"]}
        for expected in GOB_JOBS.values():
            for path in (expected["spec"], expected["model"]):
                with self.subTest(path=path):
                    row = entries[path]
                    self.assertEqual(row["classification"], "public")
                    self.assertEqual(row["license"], "BSD-3-Clause")
                    self.assertEqual(row["sha256"], _sha256((ROOT / path).read_bytes()))


if __name__ == "__main__":
    unittest.main()
