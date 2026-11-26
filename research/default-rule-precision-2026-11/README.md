# Precision of two noisy default rules

Measured on 2026-11-26 with the Bifrost 0.15.4 `aarch64-apple-darwin` release.
That is the version pinned in `policy-authoring.json`; its SHA-256 was checked
against the GitHub release digest.

## Why

From a prod Loki review of `check finished` events over the seven days to
2026-11-25 (Bifrost 0.15.4, 3,847 analyses):

| Rule | Analyses with a finding | Findings |
| --- | --- | --- |
| `bifrost.correctness.identical-conditional-branches` | 927 (24%) | 1,985 |
| `bifrost.correctness.empty-failure-handler` | 895 (23%) | 2,284 |

bifrost-service already limits `empty-failure-handler` to production code in
checks (`PRODUCTION_ONLY_IN_CHECKS`). `identical-conditional-branches` has no
such limit. It is also slow in prod: p95 60 s, and 185 runs went over its
120 s budget. We have no access to user feedback in the prod DB, so precision
here comes from hand-labelling findings on public repositories.

## Sample

Nine repositories, shallow clones of the default branch:

| Repository | Language | Commit |
| --- | --- | --- |
| psf/requests | Python | `3c7baaa05ab4aa49cc819ce3a819d260de19c157` |
| pypa/pip | Python | `5b4d45102eb54ceb77740f83c80ef09017565a67` |
| axios/axios | JavaScript | `a35e6f4ee55dcdec8c7b6f15218d636754c06c66` |
| honojs/hono | TypeScript | `9c2f2948498434506f9ebc77a213bf67a2da5603` |
| gin-gonic/gin | Go | `0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646` |
| caddyserver/caddy | Go | `679806f92d49e5b494200f2e90a93f228203a418` |
| google/gson | Java | `d9b5079eaa4567219771bba6d04289cf45c7589b` |
| google/guava | Java | `cdb3863e02e9e728848727b3c132f94f8c22cd26` |
| BurntSushi/ripgrep | Rust | `3e85c6c148fdce38a99ceeb9d2780dc7b03b4a4f` |

Each rule ran on its own:

```bash
bifrost --root . --no-builtin-policies --policy-file .probe/<rule>.rqlp \
  --format json --policy-timings --fail-on never --no-incremental
```

[`labels.csv`](labels.csv) holds every label, with the repository commit,
path, line, arm ordinals (identical-conditional-branches only), label, shape
and a short note.

### What counts as a true positive

- **identical-conditional-branches:** the pair is worth a reviewer's comment.
  The arms could be merged or the duplication hints at a copy/paste slip. A
  pair is a false positive when merging would mean reordering the conditional
  (another arm sits between the two), when each arm deliberately carries its
  own rationale comment, when the language construct blocks a plain merge, or
  when the engine's "identical" is wrong.
- **empty-failure-handler:** the handler swallows a failure and gives the
  reader no sign that this is deliberate. The ESLint `no-empty`, Sonar S108
  and PMD `EmptyCatchBlock` (`allowCommentedBlocks`) conventions apply: a
  comment inside the handler states intent, and so does a binding named like
  `ignored` (the IntelliJ convention). The Python optional-import fallback
  (`except ImportError: pass`) also counts as intent. Narrow EAFP handlers
  without a comment (`except KeyError: pass`) are labelled true positives. A
  reviewer may well accept them, but nothing in the code says they were
  considered.

## identical-conditional-branches

All 73 findings were labelled, because checks report this rule on test code
too (57 production, 16 test).

| Shape | TP | FP |
| --- | --- | --- |
| Adjacent arms that could be merged | 23 | |
| Non-adjacent arms with disjoint conditions (reordering is safe) | 1 | |
| Non-adjacent arms: merging would reorder past a different arm | | 31 |
| Outer pair of a run of three equal arms, already reported as 0:1 and 1:2 | | 2 |
| Arms that each carry their own rationale comment | | 6 |
| Go else-if try chain (`if ok, err = a(); ok {…} else if ok, err = b(); ok {…}`) | | 5 |
| Python string literals with escapes compared as equal (engine defect) | | 3 |
| Empty arms that hold only `TODO` comments | | 2 |
| **Total** | **24** | **49** |

Precision is **33% (24/73)**.

The largest group, 33 of 49 false positives, is "not adjacent": for example
`if a: discard("source") elif b: discard("binary") elif c: discard("source")`.
Reporting only pairs with no arm between them would keep 23 true positives and
16 false positives, **59% precision**, and cut the findings from 73 to 39.

Guard clauses are not a separate shape here. Every `return False` or
`return None` guard pair in the sample was also non-adjacent. No logging-only
pairs turned up.

### Why the pack can't fix this on 0.15.4

Two pack-only versions of "adjacent only" were built and measured. Neither is
shippable:

1. **Left join plus absence.** The draft joined each proven pair to every row
   of the same conditional and earlier arm, then asserted that no row ends
   before the pair. It passed a complete fixture but reported **nothing** on
   all nine repositories. Real workspaces always have some `open` branch rows,
   and an absence assertion (`:cardinality (at-least 1)`) is withheld for the
   whole run when the row set is incomplete. It was also about 1.7× slower on
   guava (90 s against 49–55 s).
2. **Literal pair enumeration.** A union of `(filter ((earlier_ordinal eq i)
   (later_ordinal eq i+1)) …)` arms for pairs (0,1) to (13,14), plus one
   fallback arm. Union and query-plan limits (16 branches, 64 nodes) force a
   single multi-language seed and cap the pairs. The evaluation work seems to
   be shared (gson evaluation went from 4.1 s to 4.7 s), but each arm is
   charged against `query.max_scanned_source_bytes` separately. On guava the
   run was refused at the 134 MB grant, scanned 1,667 of 2,111 files, and
   silently lost two true positives. A shorter enumeration would only move
   that cliff to a larger repository.

The row predicate language has `(field X)` comparisons but no arithmetic and
no `or`. A policy allows only one assertion, and every binding must be joined.
So adjacency needs engine support. The policy is unchanged in this PR. The
probe sources are kept in [`icb-probe/`](icb-probe/) for the engine issue:
seven adjacent positives and seven non-adjacent near misses in Python,
JavaScript and Go.

## empty-failure-handler

512 findings in all. 160 are on production paths, which is what checks
report: 352 are under test directories or in guava-testlib. 60 production
findings were drawn with `random.seed(20261125)`.

| Shape | TP | FP |
| --- | --- | --- |
| Comment inside the handler explains the ignore | | 24 |
| Python optional import (`ImportError`, `ModuleNotFoundError`) | | 8 |
| Explanation sits just outside the handler (above `except`, or in the `try` body) | | 2 |
| Silent narrow handler (`KeyError`, `FileNotFoundError`, …) | 19 | |
| Silent broad handler (`except Exception`, a broad tuple) | 4 | |
| Silent JavaScript or TypeScript catch-all (`catch {}`) | 3 | |
| **Total** | **26** | **34** |

Precision is **43% (26/60)**.

Across all 512 findings, binding names were a strong intent signal outside
the random sample: `tolerated` (212), `expected` (26), `ignored`/`ignore` (17)
and `_` (4). Most of these are in guava-testlib, which ships as a library under
`src/` and so may count as production code.

The task also asked about other shapes:

- **`KeyboardInterrupt`:** no empty `except KeyboardInterrupt` appeared in any
  of the nine repositories.
- **`StopIteration`:** appeared twice, the same requests code and its vendored
  copy in pip.
- **Go `_ =` patterns:** the rule doesn't select `_ = f()` at all, because it
  is not a failure branch. Go produced only three findings, in caddy's
  `context_test.go`. Each is an `if err != nil {}` whose comment says the
  error *should* be handled. Rust produced none.

### Change

Catch-clause seeds that state an intent are left out before the handler state
is classified:

- a comment inside the clause;
- a binding named `_`, `ignore`, `ignored`, `expected` or `tolerated`;
- a Python clause that names `ImportError` or `ModuleNotFoundError`, unless it
  also names `Exception` or `BaseException`.

A `TODO`, `FIXME` or `XXX` comment in the clause keeps it reported, whatever
the binding or caught type says.

These are pattern negations on each `catch` node. They are not an `except` set
difference: a set difference over the catch set is withheld as a whole when
parser recovery leaves any selected catch without a fact. That draft reported
0 of guava's 366 findings because of one recovered region in
`EqualsTester.java`.

Results:

| | Before | After |
| --- | --- | --- |
| All findings | 512 | 104 |
| Production findings | 160 | 63 |
| Sample precision | 43% (26/60) | **93% (25/27)** |

- **Lost true positive:** one, a handler whose only comment is a
  `# noqa: PERF203` lint directive.
- **Remaining false positives:** two, where the explanation sits outside the
  clause.
- **By repository (production):** axios 11 → 1, gson 8 → 0, guava 36 → 2 (the
  two left are `TODO` handlers), hono 15 → 7, pip 84 → 52, requests 6 → 1.

The fixture is
[`fixtures/policy/bifrost.code-smells/empty-failure-handler`](../../fixtures/policy/bifrost.code-smells/empty-failure-handler/README.md):
17 positives, and 15 near misses that the old policy reported.

## Runtime on the largest repository (guava)

Five consecutive `--no-incremental` runs of each policy on guava (2,218
files, about 21 MB of scanned source). p95 is the nearest-rank value, so with
five runs it is the slowest.

| Policy | Wall time, five runs (s) | Median | p95 | Evaluation stage (s) |
| --- | --- | --- | --- | --- |
| identical-conditional-branches (unchanged) | 58.4, 91.0, 97.9, 116.0, 99.6 | 97.9 | **116.0** | 52–103 |
| empty-failure-handler, before | 16.3, 15.9, 14.2, 18.4, 14.7 | 15.9 | **18.4** | 4.3–6.1 |
| empty-failure-handler, after | 15.6, 16.1, 13.5, 22.8, 12.0 | 15.6 | **22.8** | 3.9–9.8 |

Another session's release dry-run shared the CPU during these runs, so the
spread is wide. The 22.8 s run is one outlier; the medians of the two
empty-failure-handler versions are the same. identical-conditional-branches
spends almost all of its time in `policy_evaluation` (the `branch-relations`
derivation), not in registration. Its guava p95 of nearly two minutes matches
the prod p95 of 60 s and the 185 runs over the 120 s budget.

## Engine follow-ups

These are drafted for bifrost-dev and not opened yet:

1. **P1:** `branch-relations` should expose whether a pair is adjacent, or
   take an `:adjacent-only` option, so identical-conditional-branches can drop
   non-adjacent pairs.
2. **P1:** Python string literals that contain an escape sequence compare
   equal in `branch-relations` whatever their other characters.
   `out.write("a\n")` and `out.write("b\n")` are reported as identical arms.
   JavaScript, Go and Rust are not affected.
3. **P2:** a run-wide incompleteness (an unrelated `open` row, or one
   recovered region) withholds every absence-style assertion and every
   `except` result, even for groups the incomplete rows can't touch.
4. **P2:** a union of filters over an identical subquery charges each arm
   against the scanned-bytes budget, although the work appears to be shared.

## Caveats

- One person labelled every finding, and the TP/FP boundary for narrow EAFP
  handlers is a judgement call. `labels.csv` keeps the shape of every finding
  so that it can be reweighed.
- Path classification as production or test is a heuristic (test
  directories, `_test.go`, `*.test.ts`, `*Test.java`, `test_*.py`).
- Timings come from a shared laptop. Other sessions were running at the same
  time.
