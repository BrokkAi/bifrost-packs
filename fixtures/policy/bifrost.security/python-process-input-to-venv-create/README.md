# Python process input choosing a venv.create directory

Qualifies the version-independent part of the Python CVE lead
BrokkAi/bifrost-packs#355 (CVE-2024-9287). `venv.create(env_dir)` makes
`env_dir`, writes an interpreter, activation scripts and `pyvenv.cfg` into it,
and with `clear=True` first deletes its contents. On affected interpreters the
activation scripts also embed `env_dir` without shell quoting, so a crafted
directory name runs commands when someone sources `bin/activate`. A process
input that reaches `env_dir` chooses where executables are written and what is
cleared on any CPython version. The affected-version part needs CPython
interpreter evidence, which Bifrost 0.15.1 does not publish
(bifrost-dev#3867).

Sources are the reviewed `os.environ` and `sys.argv` keyed reads of
`bifrost.security.python.process-input-to-os-system`. The sink is formal 0 of
`member.python.venv.create`, added in
`bifrost.python-stdlib-api-declarations` 0.7.0, with a complete summary (an
`escape` of `env_dir` and of `prompt`, no transfers) added in
`bifrost.python-security-sink-summaries` 0.6.0. Both are copied into
`.bifrost/semantic-models`. The policy uses `require-model`.

The policy is opt-in (`"activation": "opt-in"`) for two engine defects in
Bifrost 0.15.1:

- A keyword argument that skips a defaulted positional formal, such as
  `venv.create(path, with_pip=True)`, fails the whole run with
  `internal_invariant` ("external summary aliases require one synthetic
  unmaterialized call shape"). This is bifrost-dev#9991, fixed upstream after
  0.15.1. `venv.create(env_dir=...)` and positional flags are proven. The
  fixture keeps the failing shape out; it is recorded in
  `research/osv-dataflow-2026-11/python/probe/355-venv`.
- A process input read after any other call in the same procedure is not
  selected (bifrost-dev#9999), which leaves ordinary code inconclusive. The
  lookalike case reads its input before constructing the local class for that
  reason.

## Cases

- **Positives** (`main.py`, lines 10, 16, 21, 26): `venv.create(sys.argv[1])`,
  `os.environ["BUILD_ENV_DIR"]` through a local into `create` imported with
  `from`, `venv.create(sys.argv[1], False, True)` (positional `clear`) and
  `venv.create(env_dir=os.environ["BUILD_ENV_DIR"])`.
- **Near misses**: a constant directory (`main.py`), a constant directory with
  positional flags beside an unused `sys.argv` read (`main.py`), and a local
  class instance named `venv` whose `create` method receives the input
  (`lookalike.py`).
- **Incomplete** (`incomplete/`, its own workspace; `.bifrostignore` keeps it
  out of the parent run): `builder` calls `venv.EnvBuilder(...).create(...)`
  (`EnvBuilder` is not modeled) and `helper` passes the input through an
  unresolved helper. Both report nothing and stay inconclusive.

## Validation

Bifrost `v0.15.1` (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, build identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), with the `packs/v0.11.0` native bundle (`bifrost.public.packs-0.11.0-native.tar.gz`, SHA-256 `055f25dedf45dc44bf3fe49429e3af0cd3d3d779ba75415c08956fe35a7d9695`) as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, `BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR` per run. Evaluation date 2026-11-10.

| Root | Completion | Findings |
| --- | --- | --- |
| `.` | `proven_by_summary` | 4, all definite and complete (`main.py:10`, `:16`, `:21`, `:26`) |
| `incomplete/` `--sources builder` | `inconclusive (partial_discovery)` | 0 |
| `incomplete/` `--sources helper` | `inconclusive (partial_discovery)` | 0 |

Policy hash `52a10aaaa0589363950399d328b298299a957bf129e1295772160f8a99c2e251`.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/process-input-to-venv-create.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-10
```
