# `python-split-file-extension` fixture

Exercises `bifrost.correctness.python-split-file-extension` (BrokkAi/bifrost-packs#458).

Validated with the Bifrost 0.15.4 `aarch64-apple-darwin` release (archive SHA-256 verified, build `ea8da845e8d7`, the same build identity as the Linux CLI pinned in `policy-authoring.json`) on 2026-11-25. No semantic models are needed. The run is `complete`, with no diagnostics and these definite findings:

- `positive.py:5`: `ext = filename.split(".")[1]` (assignment).
- `positive.py:12`: `file_path.split(".")[1].lower()` (receiver of a call).
- `positive.py:16`: `fname.split('.')[1] == "json"` (comparison operand).
- `positive.py:20`: `upload.filename.split(".")[1]` (field receiver).
- `positive.py:24`: `os.path.basename(path).split(".")[1]` (basename receiver).

The near misses produce no findings:

- `near_miss.py`: `os.path.splitext`, `Path.suffix`, `rsplit(".", 1)[-1]`, `split(".")[-1]`, `split(".")[0]`,
  `version.split(".")[1]`, `dotted_name.split(".")[1]`, an unindexed `split(".")`, and a split inside a
  comparison chain.

## Real code

On the pre-fix parent of PyPortfolio/PyPortfolioOpt@e12417a (`d508869f`) the rule reports
`pypfopt/base_optimizer.py:109`, the line the fix changed. At current heads of pingouin, PyPortfolioOpt, backtesting.py, networkx and bifrost-service the rule is `complete` with no findings.

## Known edges

- The receiver is recognised by name (`filename`, `fname`, `file_name`, `file_path`, `filepath`, `fpath`,
  `pathname`, `basename`, `file`, with optional prefixes such as `out_filename`), by a field with such a name, or
  by an `os.path.basename(...)` call. A path in a variable with another name, such as `path` or `p`, is not
  reported; that keeps version strings and dotted identifiers out.
- The subscript has no normalized kind on Bifrost 0.15.4. Its parent is matched by role (assignment value,
  `return`, comparison operand, call receiver or argument) and its parser-backed text, and the `split` call is
  matched structurally. Other parents, such as a dict key `writers[name.split(".")[1]]`, are not selected.
- Comparison chains expose no singular left/right roles, so the comparison arms exclude them; a split inside a
  chain is not reported.

## Reproduce

```bash
cd fixtures/policy/bifrost.code-smells/python-split-file-extension
bifrost --root . --policy-file .bifrost/policies/python-split-file-extension.rqlp --format json --fail-on never --output report.json
```

The fixture copy of the policy must match `rules/bifrost.code-smells/policies/python-split-file-extension.rqlp`.
