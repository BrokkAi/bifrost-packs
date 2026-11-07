"""Pin the compress/gzip and io native jobs (#252).

These checks pin source inputs only. Runtime behavior is recorded in
fixtures/policy/bifrost.security/go-network-read-all-unbounded/README.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts.content import read_lock


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMITS = {
    "go-stdlib-compress-gzip": "a8f1458142c44fb9a94dcf0cd63771e965238fad",
    "go-stdlib-compress-gzip-declarations": "a8f1458142c44fb9a94dcf0cd63771e965238fad",
    "go-stdlib-io": "65b68f55b537ab77b7ecd8569b0c838aac9be0ea",
    "go-stdlib-io-declarations": "21151aab8d92052e3a766620c5d531f92bf87089",
}
JOBS = {
    "go-stdlib-compress-gzip": {
        "pack_id": "bifrost.go.stdlib.compress-gzip",
        "completeness": "complete",
        "source": "https://pkg.go.dev/compress/gzip",
    },
    "go-stdlib-compress-gzip-declarations": {
        "pack_id": "bifrost.go.stdlib.compress-gzip-declarations",
        "completeness": "partial",
        "source": "https://pkg.go.dev/compress/gzip",
    },
    "go-stdlib-io": {
        "pack_id": "bifrost.go.stdlib.io",
        "completeness": "complete",
        "source": "https://pkg.go.dev/io",
    },
    "go-stdlib-io-declarations": {
        "pack_id": "bifrost.go.stdlib.io-declarations",
        "completeness": "partial",
        "source": "https://github.com/golang/go/blob/d90b98e65320778f3b1f99a6951ab20f04d218b3/src/io/io.go (22 exported io interfaces, their methods and embeddings, and io.ReadAll, io.Copy, io.LimitReader functions)",
    },
}
FIXTURE = ROOT / "fixtures/policy/bifrost.security/go-network-read-all-unbounded"
POLICY = "rules/bifrost.security/policies/go/network-read-all-unbounded.rqlp"
FIXTURE_MODELS = (
    "go-stdlib-net.json",
    "go-stdlib-net-declarations.json",
    "go-stdlib-os.json",
    "go-stdlib-os-declarations.json",
    "go-stdlib-compress-gzip.json",
    "go-stdlib-compress-gzip-declarations.json",
    "go-stdlib-io.json",
    "go-stdlib-io-declarations.json",
)


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _spec(name: str) -> str:
    return f"semantic-packs/go/{name}.spec.json"


def _model(name: str) -> str:
    return f"semantic-packs/models/{name}.json"


def _summaries(name: str) -> dict[str, dict]:
    payload = _load(_model(name))["shards"][0]["payload"]
    return {row["target"]["symbol"]: row for row in payload["summaries"]}


class GoReadAllNativeJobTests(unittest.TestCase):
    """Pin the gzip and io jobs, their summaries and the fixture copies."""

    def test_jobs_follow_the_gob_jobs_and_bind_their_specs(self):
        jobs = _load("native-generation.json")["jobs"]
        names = [job["name"] for job in jobs]
        start = names.index("go-stdlib-encoding-gob-declarations") + 1
        self.assertEqual(names[start:start + len(JOBS)], list(JOBS))
        for name, expected in JOBS.items():
            with self.subTest(job=name):
                job = jobs[names.index(name)]
                self.assertEqual(job, {"name": name, "spec": _spec(name), "artifact": _model(name)})
                spec = _load(_spec(name))
                model_bytes = (ROOT / _model(name)).read_bytes()
                model = json.loads(model_bytes)
                self.assertEqual(spec["pack_id"], expected["pack_id"])
                self.assertEqual(model["pack_id"], expected["pack_id"])
                self.assertEqual(spec["pack_version"], model["version"])
                self.assertEqual(model["schema_version"], 8)
                self.assertEqual(model["completeness"], expected["completeness"])
                self.assertEqual(model["license"], "BSD-3-Clause")
                self.assertEqual(spec["provenance"], {"source": expected["source"], "revision": "go1.26.0"})
                self.assertEqual(spec["notices"], ["notices/go-1.26.0-BSD-3-Clause.txt"])
                self.assertEqual(spec["artifact"]["sha256"], _sha256(model_bytes))
                self.assertEqual(
                    spec["artifact"]["url"],
                    f"https://github.com/BrokkAi/bifrost-packs/blob/{SOURCE_COMMITS[name]}/{_model(name)}",
                )

    def test_summaries_pass_the_reader_through(self):
        gzip = _summaries("go-stdlib-compress-gzip")
        self.assertEqual(set(gzip), {
            "compress/gzip.NewReader(r io.Reader)",
            "compress/gzip.Reader.Close()",
            "compress/gzip.Reader.Multistream(ok bool)",
        })
        self.assertEqual(gzip["compress/gzip.NewReader(r io.Reader)"]["transfers"], [{
            "input": {"kind": "parameter", "ordinal": 0},
            "exit_kind": "normal",
            "output": {"kind": "indexed_normal_return", "ordinal": 0},
        }])
        io = _summaries("go-stdlib-io")
        self.assertEqual(set(io), {"io.ReadAll(r io.Reader)", "io.LimitReader(r io.Reader, n int64)"})
        self.assertEqual(io["io.LimitReader(r io.Reader, n int64)"]["transfers"], [{
            "input": {"kind": "parameter", "ordinal": 0},
            "exit_kind": "normal",
            "output": {"kind": "normal_return"},
        }])
        for row in list(gzip.values()) + list(io.values()):
            with self.subTest(summary=row["id"]):
                self.assertEqual(row["completeness"], "complete")

    def test_io_copy_is_declared_but_not_summarized(self):
        # io.Copy writes into dst, which the summary schema cannot express, and
        # a complete summary with no transfers would claim it writes nothing.
        payload = _load(_model("go-stdlib-io-declarations"))["shards"][0]["payload"]
        names = {row["locator"]["symbol"] for row in payload["members"]}
        self.assertTrue({"io.ReadAll", "io.Copy", "io.LimitReader"} <= names)
        self.assertNotIn("io.Copy(dst io.Writer, src io.Reader)", _summaries("go-stdlib-io"))
        for name in ("go-stdlib-io-declarations", "go-stdlib-compress-gzip-declarations"):
            for row in _load(_model(name))["shards"][0]["payload"]["members"]:
                with self.subTest(member=row["locator"]["symbol"]):
                    self.assertTrue(row["callable_family_complete"])

    def test_fixture_copies_match_the_published_sources(self):
        for workspace in (FIXTURE, FIXTURE / "incomplete"):
            for name in FIXTURE_MODELS:
                with self.subTest(workspace=workspace.name, model=name):
                    self.assertEqual(
                        (workspace / ".bifrost/semantic-models" / name).read_bytes(),
                        (ROOT / "semantic-packs/models" / name).read_bytes(),
                    )
            self.assertEqual(
                (workspace / ".bifrost/policies/network-read-all-unbounded.rqlp").read_bytes(),
                (ROOT / POLICY).read_bytes(),
            )

    def test_new_specs_and_models_are_locked_public_bsd(self):
        entries = {row["path"]: row for row in read_lock(ROOT)["files"]}
        for name in JOBS:
            for path in (_spec(name), _model(name)):
                with self.subTest(path=path):
                    row = entries[path]
                    self.assertEqual(row["classification"], "public")
                    self.assertEqual(row["license"], "BSD-3-Clause")
                    self.assertEqual(row["sha256"], _sha256((ROOT / path).read_bytes()))


if __name__ == "__main__":
    unittest.main()
