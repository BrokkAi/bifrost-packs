# Python data-flow CVE leads on Bifrost 0.15.1

The 2026-11-09 catalog leads #346–#361 are recorded separately in
[`catalog-2026-11-09.md`](catalog-2026-11-09.md).

**Outcome: two of ten leads ship as opt-in rules. Seven are blocked by the
engine, and one is blocked on models that this repository does not have yet.**

The ten leads are CPython standard-library advisories from OSV (`PSF-*`
records), filed as BrokkAi/bifrost-packs#270 to #279. Each has a data-flow
theoretical policy: taint for nine, typestate for #279. All ten are open
placement. None of them duplicates an existing `CVE-` title in
bifrost-packs or bifrost-premium-packs.

Machine-readable results, with input hashes, are in
[`outcomes.json`](outcomes.json). The files under `probe/` are research
inputs. They are not registered pack content, and the models in their
`.bifrost/semantic-models` folders are research copies.

## Engine and inputs

- Bifrost `v0.15.1`, `bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`. Archive
  SHA-256 `4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`,
  which matches the release `.sha256`. Binary SHA-256
  `78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`. Build
  identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`. v0.15.2 was not
  released on 2026-11-05.
- Semantic packs: `packs/v0.10.0`, `bifrost.public.packs-0.10.0-native.tar.gz`,
  SHA-256 `3f39f9f5ec2d028e293a238ff796260101915e50963a44a93c812d9d02860945`.
  It was set as `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE`, with
  `BIFROST_SEMANTIC_PACK_DOWNLOAD=off`. Bifrost 0.15.1 has no built-in packs.
- Every workspace has `pyproject.toml` with
  `requires-python = ">=3.13.5, <3.13.6"`. Without it the engine rejects
  `bifrost.python-stdlib`, and the Python security sink packs only activate
  for CPython 3.13.5.
- Every run used a fresh `BIFROST_CACHE_DIR` and `--no-incremental`.

## Outcomes

| Lead | Advisory | API | Outcome | Upstream |
| --- | --- | --- | --- | --- |
| #270 | CVE-2025-15282 | `urllib.request.urlopen` | **Implemented**, version-independent part: `bifrost.security.python.process-input-to-urlopen` (opt-in) | bifrost-dev#9991, #9999, #3867 |
| #271 | CVE-2025-6075 | `os.path.expandvars` | Blocked by engine | bifrost-dev#10006, #3867 |
| #272 | CVE-2026-4519, CVE-2026-4786 | `webbrowser.open*` | **Implemented**, version-independent part: `bifrost.security.python.process-input-to-webbrowser-open` (opt-in) | bifrost-dev#9999, #3867 |
| #273 | CVE-2025-15366 | `imaplib.IMAP4.xatom` | Blocked by engine | bifrost-dev#9999, #3867 |
| #274 | CVE-2026-1502 | `http.client` `set_tunnel` | Blocked by engine | bifrost-dev#9999, #3867 |
| #275 | CVE-2026-0865 | `wsgiref.headers.Headers` | Blocked by engine | bifrost-dev#3867 |
| #276 | CVE-2026-18503 | `csv.Sniffer.sniff` | Blocked by engine | bifrost-dev#3867, #9999 |
| #277 | CVE-2024-6923 | `email` header serialization | Blocked by engine | bifrost-dev#3867, #9999 |
| #278 | CVE-2026-0864 | `configparser` write | Blocked by engine | bifrost-dev#3867, #9999 |
| #279 | CVE-2026-19553 | `SSLContext.wrap_bio` | Blocked: no reviewed `ssl` models here; not probed | none yet |

## Shared blockers

| Blocker | Issue | Leads |
| --- | --- | --- |
| No Python or CPython version evidence for policies. `(dependency-evidence)` returns no rows: `Python selected dependency publication unavailable`. `version_ranges` accepts no `cpython` ecosystem. Pack activation reads `requires-python`, but no policy can. | [bifrost-dev#3867](https://github.com/BrokkAi/bifrost-dev/issues/3867) (existing; 0.15.1 repro added) | The version-gated part of every lead; all of #275 to #278 |
| A `sys.argv` or `os.environ` keyed-read source is not selected when any modeled call runs before it in the same procedure. The selector reports `Incomplete { codes: [] }` and no rows. Reading the input first proves the same flow. | [bifrost-dev#9999](https://github.com/BrokkAi/bifrost-dev/issues/9999) (new) | #273, #274, #276 to #278 (client object built first); limits #270 and #272 |
| `urlopen(url, timeout=5)` fails the whole run with `internal_invariant`: `external summary aliases require one synthetic unmaterialized call shape`. `urlopen(url, None, 5)` is proven, and `webbrowser.open(url, new=2)` is proven too. | [bifrost-dev#9991](https://github.com/BrokkAi/bifrost-dev/issues/9991) (new) | #270 |
| `import os; os.path.expandvars(x)` and `import posixpath; posixpath.expandvars(x)` stay `dispatch outcome=unproven, coverage=open`. `from os.path import expandvars` and `import os.path` are proven. | [bifrost-dev#10006](https://github.com/BrokkAi/bifrost-dev/issues/10006) (new) | #271 |

## Shipped rules

Both rules reuse the sources of the shipped
`bifrost.security.python.process-input-to-os-system`. Those are `os.environ`
and `sys.argv` keyed reads, bound through the import binder and the reviewed
`bifrost.python-process-inputs` model. Both rules use `:call-modeling
(call-modeling :unmodeled require-model)`, and both are opt-in.

- **#270 `process-input-to-urlopen`.** The sink is formal 0 of
  `member.python.urllib.request.urlopen`, from the existing reviewed models.
  The fixture is `proven_by_summary` with 3 definite findings. The near misses
  are a constant URL, an unused `sys.argv` read and a workspace `urlopen`
  lookalike. Reading the response (`.read()`) and an unresolved helper are
  inconclusive. The `timeout=` keyword failure is why the rule is opt-in.
- **#272 `process-input-to-webbrowser-open`.** The sinks are formal 0 of
  `webbrowser.open`, `open_new` and `open_new_tab`. Their declarations and
  complete summaries are new in this change (see below). The fixture is
  `proven_by_summary` with 5 definite findings, including `new=2` by keyword.
  `webbrowser.get().open(...)` and an unresolved helper are inconclusive.

### Model changes

- `bifrost.python-stdlib-api-declarations` 0.5.0 → **0.6.0** adds the
  `webbrowser` module type and `open(url, new, autoraise)`, `open_new(url)` and
  `open_new_tab(url)`, with `callable_family_complete`. The signatures follow
  the pinned typeshed `webbrowser.pyi`.
- `bifrost.python-security-sink-summaries` 0.4.0 → **0.5.0** adds one complete
  summary per function: one `escape` of `url` and no transfers.

The `expandvars` and `imaplib` models stay in `probe/`. Their rules can't ship
until bifrost-dev#10006 and bifrost-dev#9999 are fixed, so the models aren't
promoted.

## Per-lead notes

- **#271:** The CPU-cost CVE is version-gated. The version-independent slice
  is environment disclosure through an attacker-controlled template (CWE-526),
  and it works only for the less common import spellings.
- **#273:** With research `IMAP4` models, `xatom(sys.argv[1])` is proven when
  the input is read before the constructor (`probe/273-imaplib/argv-first`).
  In the usual order the source vanishes (bifrost-dev#9999).
- **#274 to #278:** These were not probed separately. Each needs new class
  models (`http.client`, `wsgiref.headers`, `csv`, `email.message`,
  `configparser`). Each constructs its object before the tainted write, which
  is the #273 shape. #275 also needs WSGI `environ` request sources, and #277
  and #278 need same-object write-then-serialize tracking.
- **#279:** The blocker is content in this repository. There are no reviewed
  `ssl.create_default_context` or `SSLContext.wrap_bio` models, and no model
  for `check_hostname` writes. The defaulted-`server_hostname` filter already
  exists (`binding_kind defaulted`, as `insecure-default-protocol` uses).
  Whether typestate can carry `check_hostname` from the factory to `wrap_bio`
  is unverified, so no engine issue was filed.

## Side observation

The shipped `bifrost.security.python.xml-bomb` fixture is `not_run` on 0.15.1
with packs 0.10.0: `qualified call locator xml.dom.minidom.parseString resolved
to multiple exact identities`. The two identities are the `bifrost.python-stdlib`
typeshed member and `member.python.xml.dom.minidom.parse-string`. It is outside
these leads and is recorded here for follow-up.
