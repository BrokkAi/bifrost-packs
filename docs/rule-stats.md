# Generated rule inventory

The README summary and [full rule catalog](rule-catalog.md) are generated from
policy documents under `rules/` and their catalog manifests. Only stable policy
IDs count as rules. Test helpers, research probes, endpoint files and semantic
models are excluded. This report describes this checkout's source inventory;
release selection and scanner enablement remain separate.

```sh
python3 tools/rule_stats.py --write
python3 tools/rule_stats.py --check
python3 tools/rule_stats.py --json > /tmp/rule-stats.json
```

The generator uses the Python standard library, runs offline, and does not
build or invoke Bifrost. It changes only the marked README block and generated
catalog. Output is sorted and omits timestamps and commit hashes so unchanged
inputs produce unchanged tables. Keep the checkout's commit identity alongside
an exported report when citing a particular snapshot.

Language support and primary categories come from explicit catalog manifest
fields. A rule can count in multiple language rows; those rows are not an
additive rule total. Inline RQL `language` scopes are reported separately when
support is undeclared; they describe query syntax, not support qualification.
Tags are topic labels. Available case manifests count positive versus zero
expected findings; their presence says nothing about execution or completeness.
Absent case manifests do not mean absent tests elsewhere. Use the existing
engine qualification workflows for exact-build behavior evidence.

## Optional pre-commit hook

For a repository without an existing hook configuration, opt in with:

```sh
git config --local core.hooksPath .githooks
```

This repository setting also applies to its linked worktrees.

If you already use hooks, invoke `python3 -B tools/check_rule_stats_staged.py`
from your existing pre-commit hook instead. The checker snapshots the Git index
in a temporary directory and checks the staged generator, policies, manifests
and documentation together. It does not modify or stage files. On failure,
regenerate, review the diff, and stage the intended documentation with the rule
changes. This preserves partial staging.

CI runs the same generator with `--check` on the checked-out commit, so README
drift is caught even in checkouts where the optional local hook is not enabled.
