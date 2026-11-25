# Python process input reaching webbrowser.open

Qualifies the version-independent part of the Python CVE lead
BrokkAi/bifrost-packs#272 (CVE-2026-4519 and its incomplete fix
CVE-2026-4786). `webbrowser.open`, `open_new` and `open_new_tab` hand the URL
to the platform browser or URI handler, and the advisory tells callers to
sanitize URLs before calling them. A process input that reaches the `url`
argument chooses the local handler on any CPython version; on affected
interpreters a leading dash also becomes a browser option. That
affected-version part needs CPython interpreter evidence, which Bifrost 0.15.1
does not publish (bifrost-dev#3867).

Sources are the reviewed `os.environ` and `sys.argv` keyed reads of
`bifrost.security.python.process-input-to-os-system`. The sinks are formal 0 of
`member.python.webbrowser.open`, `open_new` and `open_new_tab`, added in
`bifrost.python-stdlib-api-declarations` 0.6.0, with complete summaries (one
`escape` of `url`, no transfers) added in
`bifrost.python-security-sink-summaries` 0.5.0. Both are copied into
`.bifrost/semantic-models`. The policy uses `require-model`.

The policy is opt-in (`"activation": "opt-in"`), because a process input read
after any modeled call in the same procedure is not selected
(bifrost-dev#9999), which leaves ordinary code inconclusive.

## Cases

- **Positives** (`main.py`, lines 8, 13, 17, 21, 25): `webbrowser.open(sys.argv[1])`,
  `os.environ["HELP_URL"]` through a local into `open_new` imported with
  `from`, `open_new_tab(sys.argv[1])`, `open(sys.argv[1], new=2)` and
  `open(sys.argv[1], 2, False)`.
- **Near misses** (`main.py`): a constant URL, and a constant URL beside an
  unused `sys.argv` read.
- **Incomplete** (`incomplete/`, its own workspace; `.bifrostignore` keeps it
  out of the parent run): `controller` calls `webbrowser.get().open(...)`
  (controller classes are not modeled) and `helper` passes the input through an
  unresolved helper. Both report nothing and stay inconclusive.

## Validation

Bifrost `v0.15.1` (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, binary SHA-256 `78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`, build identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), with the `packs/v0.10.0` native bundle (`bifrost.public.packs-0.10.0-native.tar.gz`, SHA-256 `3f39f9f5ec2d028e293a238ff796260101915e50963a44a93c812d9d02860945`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-05.

| Root | Completion | Findings |
| --- | --- | --- |
| `.` | `proven_by_summary` | 5, all definite and complete (`main.py:8`, `:13`, `:17`, `:21`, `:25`) |
| `incomplete/` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/` `--sources controller` | `inconclusive` | 0 |
| `incomplete/` `--sources helper` | `inconclusive` | 0 |

Policy hash `eb87578a05c78e883000073e5530846f6529e4843e54c670abd324cc9fb81c8f`.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/process-input-to-webbrowser-open.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-05
```
