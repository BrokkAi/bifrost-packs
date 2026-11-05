# Python process input reaching urllib.request.urlopen

Qualifies the version-independent part of the Python CVE lead
BrokkAi/bifrost-packs#270 (CVE-2025-15282). `urllib.request.urlopen` opens a
URL with the default opener, which dispatches on the URL scheme, so a process
input that reaches its `url` argument picks a local file (`file:`), an
internal host or a `data:` URL on any CPython version. The CVE's
header-injection part needs CPython interpreter evidence, which Bifrost 0.15.1
does not publish (bifrost-dev#3867).

Sources are the reviewed `os.environ` and `sys.argv` keyed reads of
`bifrost.security.python.process-input-to-os-system`. The sink is formal 0 of
`member.python.urllib.request.urlopen`. Both bind through the reviewed models
copied into `.bifrost/semantic-models`
(`bifrost.python-stdlib-api-declarations` 0.6.0 and
`bifrost.python-security-sink-summaries` 0.5.0) and the bundled
`bifrost.python-process-inputs` 0.1.0. The policy uses `require-model`.

The policy is opt-in (`"activation": "opt-in"`). Two engine gaps make
ordinary code inconclusive or failed:

- **`urlopen(url, timeout=5)` fails the whole run** with `internal_invariant`
  (`external summary aliases require one synthetic unmaterialized call shape`).
  The positional form `urlopen(url, None, 5)` is proven. See
  bifrost-dev#9991; the repro is
  `research/osv-dataflow-2026-11/python/probe/270-urlopen/v-kw`.
- **A process input read after any modeled call** in the same procedure is
  not selected (bifrost-dev#9999).

## Cases

- **Positives** (`main.py`, lines 8, 13, 17): `urllib.request.urlopen(sys.argv[1])`,
  `os.environ["FEED_URL"]` through a local into `urlopen(url)` imported with
  `from`, and `urlopen(sys.argv[1], None, 5)`.
- **Near misses**: a constant URL (`main.py`), a constant URL beside an unused
  `sys.argv` read (`main.py`), and a workspace function named `urlopen`
  (`lookalike.py`).
- **Incomplete** (`incomplete/`, its own workspace; `.bifrostignore` keeps it
  out of the parent run): `read` reads the response (`HTTPResponse.read` is
  not modeled, so the run is inconclusive although the finding is definite and
  complete) and `helper` passes the input through an unresolved helper (no
  finding, inconclusive).

## Validation

Bifrost `v0.15.1` (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, binary SHA-256 `78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`, build identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), with the `packs/v0.10.0` native bundle (`bifrost.public.packs-0.10.0-native.tar.gz`, SHA-256 `3f39f9f5ec2d028e293a238ff796260101915e50963a44a93c812d9d02860945`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-05.

| Root | Completion | Findings |
| --- | --- | --- |
| `.` | `proven_by_summary` | 3, all definite and complete (`main.py:8`, `:13`, `:17`) |
| `incomplete/` | `inconclusive (partial_discovery)` | 1 definite (`read/main.py:6`) |
| `incomplete/` `--sources read` | `inconclusive` | 1 definite |
| `incomplete/` `--sources helper` | `inconclusive` | 0 |

Policy hash `3f6c8cfbf567367dbd3e82b9852c25ac7c70ebe1cb368024381de5acba8fa9f3`.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/process-input-to-urlopen.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-05
```
