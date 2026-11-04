# `py/failed-inheritance-inference`

Reports each definite unresolved or non-class base expression. The class hierarchy stays open when base inference fails, so **runs report inconclusive when inference fails**; downstream hierarchy-dependent checks must retain that uncertainty.

## Validation

- Validated with a Bifrost 0.12.0 development build (`bifrost --build-identity` prints a61cdcc7ea892570a3f99c6be1981442f22a6140), evaluation date 2026-10-08.
- Command, run from this directory: `bifrost --root . --policy-file .bifrost/policies/failed-inheritance-inference.rqlp --no-builtin-policies --format json --evaluation-date 2026-10-08`.
- Completion: `Inconclusive` (`capability_incomplete`), as designed; policy hash `7246bd0332ef61fd1c07a1e9b1e08eaeb071239fbf4bb120781c471ccca5d77c`.
- Definite findings: `engine_cases.py:9` (`MissingName`), `engine_cases.py:13` (`CallResult`), and `engine_cases.py:20` (`DynamicValue`). Resolved local and imported bases are clean.
- No semantic model is required.

The policy reports definite base failures while keeping unknown hierarchy incomplete, using the `inference_failure` and `coverage=complete` constraints. Source query: `python/ql/src/analysis/TypeHierarchyFailure.ql`, CodeQL commit `ae741615f3e178ce61289a651790dc67fcc18e19`.


## Upstream-test gate

The pinned CodeQL analysis/TypeHierarchyFailure.ql has no upstream query-test .expected suite, source fixture, or version variant under python/ql/test/query-tests/. Therefore there are no upstream cases to run or compare (FP 0, FN 0, abstentions 0). The campaign fixture continues to report its three definite inference failures and correctly leaves the run Inconclusive; the manifest severity_rationale states that runs report inconclusive when inference fails.
