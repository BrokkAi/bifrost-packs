# CodeQL upstream-test gate

A shared measuring instrument for policy parity, using Python 3.10+ and only
its standard library. Run the scripts with `python3 -I`; no installed package,
network, inventory file, or host-specific toolchain path is needed. Inputs are
read-only. Upstream tests are read from a caller-supplied CodeQL checkout;
none are vendored here. The small fixtures under `tests/fixtures/codeql_gate`
are authored examples.

The seed was a Java parity gate. This implementation generalizes its oracle,
run isolation, union of report runs, diagnostics, locked TSV summary, and
cleanup. This harness and its authored fixtures are Apache-2.0.

## Interface

```sh
python3 -I scripts/upstream/codeql_gate/gate.py expected go/duplicate-branches \
  --codeql-root "$CODEQL_ROOT" \
  --test-dir go/ql/test/query-tests/RedundantCode/DuplicateBranches

python3 -I scripts/upstream/codeql_gate/gate.py run go/duplicate-branches \
  rules/bifrost.go-codeql-quality/policies/duplicate-branches.rqlp \
  --codeql-root "$CODEQL_ROOT" --binary "$BIFROST_BINARY" \
  --state-dir "${CODEQL_GATE_STATE:-/tmp/codeql-gate}" --timeout 600
```

Commands: `expected QUERY`, `prepare QUERY`, `run QUERY POLICY`, `summary`.
`--test-dir` is relative to the checkout and repeatable; omitted directories
are discovered from matching `.qlref` files. `--query-path` overrides query
resolution by `@id` in `<language>/ql/src`. Only exact query paths or their
slash-delimited suffixes match references. Each reference uses its own
basename's `.expected`, never a different query's output. Missing references
or expected files are errors. `CODEQL_ROOT` and `BIFROST_BINARY` environment
variables are alternatives to their flags. There are no default binary or
checkout locations. State defaults to `/tmp/codeql-gate`, overridden by
`CODEQL_GATE_STATE` or `--state-dir`. Language defaults to Go.

`--extra-policy FILE` is repeatable; all policy files run in one invocation
and findings from **every** `runs[*]` are unioned for scoring. Policy basenames
must be distinct. `--models DIR` copies the complete tree into
`.bifrost/semantic-models` and enables `BIFROST_WORKSPACE_SEMANTIC_MODELS=on`.
Without it workspace models are explicitly disabled. `--keep` retains the
private root and caches; otherwise they are removed even on timeout. Logs,
exit status, `result.json`, and `result.md` remain in the unique run directory.
`results.tsv` appends under a file lock. Exit status is 0 only for PASS, 1 for
a scored failure, and 2 for setup/usage errors. `summary` lists the latest
result per query/policy, optionally filtered by `--label`.

The stager protocol is one class per language:

```python
prepare(test_dir, codeql_root, cache_dir) -> PreparedRoot
run_env(run_dir, prepared) -> dict[str, str]
extra_policy_files(prepared) -> list[Path]
```

`PreparedRoot` carries `root: Path`, `source_paths: tuple[str, ...]`, and an
optional `staged_artifacts` list for language-specific artifact coordinates and
provenance. Coverage is measured independently by the core. An optional
`inline_oracle(test_dir, query_id)` supplies language-specific annotations
for the query being scored.
The core owns ordinary private file copies, policy placement, model copying,
execution, process-group timeout, scoring, provenance and output. Prepared
Go roots are keyed by absolute test directory, staged paths/content hashes,
and stager version, built in a temporary sibling and published by atomic
rename. Concurrent preparations discard the losing temporary directory.
Prepared roots are never modified by runs.

## Go staging and module choice

Go copies all non-CodeQL files recursively, excluding `*.expected`, `*.qlref`,
`*.ql`, and files named `options`. Existing `go.mod`, `go.sum`, `vendor/`, and
build-tagged Go sources are preserved byte for byte. A missing root `go.mod`
gets this synthetic module:

```go
module codeql.test/fixture

go 1.18
```

This prevents ambient parent modules from changing Bifrost's dependency
selection and gives standalone tests a stable identity. Version 1.18 permits
generic Go fixtures without requesting a toolchain download; an existing
module's version always wins. This is a staging choice, not a claim that
CodeQL uses this module identity. The pinned CodeQL checkout's
`go/codeql-extractor.yml` explicitly enables `legacy_qltest_extraction: true`;
its standalone DuplicateBranches test has neither `go.mod` nor `options`.
These tests are accepted as legacy test directories rather than requiring a
user module. The extractor implementation/CLI is not present in the supplied
checkout or local toolchain, so its exact synthetic package/module naming
could not be verified offline. Tests depending on that identity need explicit
module staging before drawing parity conclusions. No extractor behavior is
inferred from a successful Bifrost run.

Runs set fresh `XDG_CACHE_HOME`, `BIFROST_CACHE_ROOT`, semantic-pack cache,
HOME/USERPROFILE, `GOCACHE`, and `GOMODCACHE` under the run directory;
`BIFROST_OPEN_PACKS_DISABLE=1`, `BIFROST_PARALLELISM=4`, and
`RAYON_NUM_THREADS=4`. `GOFLAGS=-mod=vendor` when vendor exists, otherwise
empty (ambient flags cannot change staging). `GOPROXY=off`, `GOSUMDB=off`, and
`GOTOOLCHAIN=local` keep execution offline. The command runs with `nice -n 10`:

```text
<bifrost> --root <private-copy> --no-builtin-policies \
  --policy-file .bifrost/policies/<name> [--policy-file ...] --format json
```

## Java staging

Java copies all non-CodeQL files recursively, reads stub paths from `options`,
and stages each referenced stub coordinate as binary and sources jars in a
fake Maven repository beneath the prepared-root cache. All stub sources go in
the sources jars. Stub sources for one test are compiled together with
`javac --release 21` from `JAVA_HOME` (or `--java-home`); compilation is best
effort, with compiler failures recorded in `compile.txt` and any emitted class
files retained in the binary jars. Sources in packages owned by the selected
JDK are listed in the compile record and excluded from compilation. Each
prepared root gets a `pom.xml` with compile dependencies for its stubs. The
binary jar is staged even when empty because Maven coordinate discovery requires
that path before it can attach the sources jar. Maven HOME and USERPROFILE point
at the fake Maven home. Coordinate evidence is kept in
`stagers/java_stub_coordinates.tsv`; unrecognized coordinates remain explicitly
marked as unknown. The per-run `result.json` records every selected artifact's
coordinates, confidence and evidence, including unknown placeholder coordinates.

```sh
python3 -I scripts/upstream/codeql_gate/gate.py run java/missing-override-annotation \
  rules/bifrost.java-codeql-quality/policies/missing-override-annotation.rqlp \
  --language java --codeql-root "$CODEQL_ROOT" --binary "$BIFROST_BINARY" \
  --java-home "$JAVA_HOME" --test-dir java/ql/test/query-tests/MissingOverrideAnnotation
```

## Oracle and classes

The first column of `#select` is the primary alert span. For a headerless
problem query, rows before the first section header are selects. Bare headings
(such as `models`) also end the select section; model rows never become alerts. `edges`,
`nodes`, `subpaths`, model sections and `testFailures` never add alerts.
Nonempty `testFailures` makes the oracle unreliable and the run ERROR.
Locations are full test-directory-relative paths and start lines; duplicate
rows at a site collapse to a set, retaining the widest expected span.

Go `//` annotations are lexed outside quoted strings, runes, raw strings and
block comments. Each stager finds its language's comments; the core reads
their contents with CodeQL's inline expectation grammar
(`shared/util/codeql/util/test/InlineExpectationsTest.qll`): a comment whose
contents start with `$ ` holds expectations up to a `//` or `#` remark, each
`MISSING:` or `SPURIOUS:` opens a column that runs to the next one, and a
column holds whitespace-separated `tag(,tag)*(=value)?` items, so
`$ Source Alert` and `$ Alert[go/a], Alert[go/b]` carry two tags each.
`Alert` and `hasTaintFlow` add an expected alert on their own line;
`Source`, `Sink` and `RelatedLocation` are path endpoints or related
locations and do not add alerts. A tag qualified with a query id, such as
`Alert[go/command-injection]`, counts only for that query, and an
unqualified tag counts for every query of the test directory, as in CodeQL;
this matters where several queries share one directory and qualify their
tags (Go CWE-078 has command-injection and stored-command together).

CodeQL matches a tag on line L to a result whose end line is L
(`onSameLine` in `InlineExpectationsTest.qll`), so a multi-line alert such
as a block or a method carries its tag on its last line. A tag therefore
names the `#select` rows of its file that end on its line and adds no site
of its own. A tag with no such row is a site known only by its end line; it
matches a finding whose end line is L (or, under `span_overlap`, a finding
that covers L), and it never merges with a row that starts on L. SPURIOUS
and MISSING tags resolve the same way, so a SPURIOUS tag on a block's
closing line marks that block's row. Expected alerts are the union of
select rows and these end-line sites. `oracle_sources` records the
contributing rows per source; `oracle_disagreement` lists `#select` rows
whose end line carries no tag and tags that name no row, when inline tags
and an expected file both exist. A disagreement is visible, never silently
reconciled by dropping one source.

`$ SPURIOUS: Alert` sites are negative examples, even if upstream `.expected`
contains them. Reporting there is always a confirmed false positive;
silence is correct. `$ MISSING: Alert` sites are known upstream omissions:
reporting is a true positive and silence is not a silent miss. These sites
are removed from the ordinary expected set and retained as separate scored
classes. These overrides also apply to tagged `hasTaintFlow` annotations,
and qualified `SPURIOUS: Alert[...]` and `MISSING: Alert[...]` tags follow
the same query-id rule.

Strict matching requires the same relative path and start line. Span overlap
is reported separately as `loose_matches`, never promoted to a strict match.
Matching is one-to-one between distinct alert sites. Unmatched findings are
false positives unless at a MISSING site or explicitly reviewed via
`--true-positives FILE`, a JSON list:

```json
[{"path":"sample.go","line":12,"justification":"Reviewed defect outside the upstream oracle"}]
```

`--anchors FILE` is a minimal, explicit per-query anchor map:

```json
{"go/example":{"line_offset":2},"go/other":{"relation":"span_overlap"}}
```

`line_offset` adds to the expected start/end lines; the default relation is
`start_line`. `span_overlap` permits overlap after the offset. It changes only
matching, not the stored oracle. Anchor configuration and reviewed true
positives are retained in the result. No automatic offset, basename matching,
or semantic similarity heuristic is applied. The duplicate-branches acceptance uses the existing Go-capable
`bifrost.code-smells` identical-conditional-branches rule without an anchor map.

## Completeness and compatibility

The observed binary emits report schema 6. Findings come from
`runs[*].findings[*].primary.path` and `primary.region.start_line/end_line`.
A finding's `completeness.type` other than `complete` prevents PASS.
`runs[*].completion.type` must be `complete` for the whole run to PASS.
`proven_subset`, `proven_by_summary`, `inconclusive`, `unsupported`, `not_run`,
missing/unknown completion types all withhold a complete verdict; `failed` is ERROR.

For an absent expected site, `completion.scope` can bound an inconclusive
run to `{"type":"files","files":[...],"truncated":false}`. That typed,
nonempty scope promises misses outside the named files have full coverage.
Missing, run-wide, empty or truncated scopes abstain globally. Otherwise,
`declared_non_exhaustive`, `finding_partial`, `run_incomplete`, and
`run_unsupported` diagnostic impacts
abstain at the diagnostic's primary file/span; an unlocated diagnostic
abstains globally. On a noncomplete run, typed completion scope is authoritative
rather than unlocated summary diagnostics widening its promised scope.
Diagnostics without an impact use conservative code-name checks. Advisory
`empty_selection` stays visible in diagnostic counts and does not convert a
complete empty run's misses to abstentions. A finding's own partial evidence
prevents PASS but does not hide silent misses elsewhere in the same file.

Report/run diagnostic or obligation truncation, omitted findings, interrupted
execution and pending policy IDs prevent PASS. Coverage asks only whether each
file carrying an ordinary expected alert was analyzed. `work.scanned_files`
is a work metric summed across selector queries, not a file inventory, and
is never used for coverage. Staged vendor, stub and build-constrained files
without expected alerts do not affect this check.

An explicit `scope.analyzed_files` list can supply the inventory (top-level,
or the intersection when every policy run provides one). Truncated lists
are not accepted as inventory. This is distinct from `completion.scope.files`,
which lists gaps and retains the run-level handling described above. The
coverage set is that explicit inventory, or the File-row and configuration
probe inventories when the report has none, unioned with paths carrying findings from every measured
policy run in the bundle. A measured finding proves its file was analyzed, even
when the probe cannot inventory that file type. This also means an unmatched
expected alert in such a file is a silent miss on a complete run. Probe findings
never contribute to measured-policy coverage. Files with neither inventory
evidence nor a measured finding remain unanalyzed and their expected alerts
abstain. The pinned schema-6 binary exposes examined procedures rather than
analyzed files, so the core uses a source File-row probe:

```lisp
(file-of (text/regex "(?s).*"))
```

The universal predicate selects source facts without a language/path filter;
`file-of` deduplicates them to files, each reported as an inventory finding.
The core also runs a configuration-fact seed. Its fact findings carry paths for
XML, JSON, properties, POM and other supported configuration documents. The
current binary does not allow `file-of` to consume `configuration_fact`, so the
seed is queried directly and its primary paths are deduplicated. Because the
seed reports one finding per configuration fact rather than one per file, a
large configuration tree can reach the report's findings cap; the omitted-findings
check then fails the probe and the gate reports ERROR. That fails closed and does
not occur on CodeQL test directories. Switch the seed to `file-of` over
configuration facts once the engine accepts that domain. Both probe
runs must complete without omission. These are file-membership checks, not
claims about a policy's semantic coverage. The source probe selects
text-bearing nodes before `file-of` deduplicates them, so an analyzed source
file that has no text-bearing node (such as an empty file) still reads as
unanalyzed unless a measured finding proves membership.
The measured policy's completion still determines whether analysis is complete.
The probe runs on the same private staged root, with the same models and
language environment and its own fresh caches/timeout. Its findings never
enter the policy's score. A complete, untruncated probe is required; failure
is ERROR. Probe stdout/stderr/exit status remain under `coverage-probe/`.

The probe inventory is cached atomically under `<state-dir>/coverage`, keyed by
prepared-root identity, binary SHA256, probe policy, model contents and the
environment variables that can change what the probe sees: the keys the stager
sets, `PATH`, and variables starting with `GO`, `BIFROST_`, `JAVA` or `RAYON_`.
Shell state such as `PWD` or `SHLVL` is ignored. A lock prevents concurrent duplicate probes. Failed
or incomplete probes are not cached. `coverage` records provenance and cache
use; `analyzed_files` records membership in the union; `unanalyzed_expected_files` lists
expected-alert files missing from that union. `coverage_unknown` means
that list is nonempty, never global abstention: only expected alerts in those
files abstain. Every expected-alert file must be analyzed for `complete`.

Pack activation's separate `packs.complete` flag is not treated as policy
execution coverage: unrelated inactive packs do not invalidate a structural
rule. Rule completion and diagnostics remain decisive.

Each ordinary expected site is matched, a silent miss under complete coverage,
or an abstention under withheld coverage. Missing runs, missing declared-policy
runs, validation errors, crashes, malformed reports, and timeouts are ERROR.
Exit code 2 is scored when the report has runs with known nonfailed completion
types, no execution termination and no pending policies; incomplete reports
normally yield abstentions. Other exit codes outside 0/1 are ERROR.
A run passes only if complete and with zero false positives, silent misses,
abstentions and errors. All directories must pass for the CLI to return 0.

Java-compatible fields remain: `query`, `test_dir`, `policy`, `extra_policies`,
`label`, `verdict`, `tp`, `fp`, `fn`, `findings`, `expected`, `loose_matches`,
`completion`, `completion_type`, `diagnostics`, `diagnostic_messages`,
`exit_code`, `wall_seconds`, `run_dir`. `fn` includes both kinds of absent
expected site for compatibility; `silent_misses` and `abstentions` separate
them. Existing EXACT/EXACT-INCOMPLETE/FP/MISS/FP+MISS/EMPTY/ERROR verdict names
remain. The new `pass` boolean is the authoritative gate result, alongside
`complete`, `query_ids`, `test_dirs`, oracle classes, `binary_sha256`, and
`codeql_commit`. `diagnostics_by_family` additionally retains actual family
counts. Multi-directory CLI output prefixes combined sites with test directory
to avoid collisions.

Changes from the seed SPEC: explicit checkout/binary arguments replace host
paths and inventory; source annotation union and known-gap classes replace
annotation count-only cross-checks; completeness-aware abstention and explicit
PASS supplement FN; prepared roots are content-keyed; copies are private
rather than hardlinked; per-run HOME replaces a shared default (a language
stager may supply a dependency HOME); process groups enforce descendant
cleanup on timeouts; models/extras/cleanup and legacy result fields remain.

## Repository SARIF comparison

```sh
python3 -I scripts/upstream/codeql_gate/compare_sarif.py \
  codeql.sarif bifrost.json mapping.json \
  --codeql-commit "$REPOSITORY_COMMIT" --bifrost-commit "$REPOSITORY_COMMIT"
```

Mapping is `{"go/query-id":"bifrost.policy.id"}`. Reports must be from the
same repository commit; callers provide both revisions and unequal values
are rejected (neither format reliably embeds the analyzed revision). Results
are per rule: matched, CodeQL-only and Bifrost-only path:start-line sets.
`_test.go` files are excluded in both directions. SARIF rule/artifact indexes,
URI escaping, and original URI bases are supported. `--repo-root` normalizes
absolute paths; paths outside it are rejected. Unmapped rules are ignored.
This is a result comparison, not a completeness/parity gate: absent results
from an incomplete repository scan still need separate review.

Run authored tests with:

```sh
python3 -B -m unittest discover -s tests -p test_codeql_gate.py -v
```
