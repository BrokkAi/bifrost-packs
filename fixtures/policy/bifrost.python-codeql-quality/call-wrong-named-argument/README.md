# call-wrong-named-argument

Mirrors CodeQL `py/call/wrong-named-argument` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.13.1, build identity 1cca9d2547b617630111c98c2d09ca01e75cd16a, engine commit bd18ba65413a14dca6d36a145cc6b11fccc57c6f. Policy hash: `cc449acaf6adc1b4129a78f77f7222edd33f91d3fa68b9d5325b824920bdb1cb`.

## Upstream gate

- Expected: 5; found: 5; abstained: 0; false positives: 0.
- Expected upstream finding lines: `upstream_wrong_arguments.py:59` (upstream line 57), `upstream_wrong_arguments.py:60` (upstream line 58), `upstream_wrong_arguments.py:61` (upstream line 59), `upstream_wrong_arguments.py:105` (upstream line 103), `upstream_wrong_arguments.py:117` (upstream line 115).
- True positives beyond CodeQL: none among upstream cases; the authored local positive is a synthetic regression case.
- Abstentions: none. The top-level run includes general analysis-incomplete diagnostics, but every expected upstream row is present.

## Fixture cases

`positive_and_near_misses.py:5` is the authored keyword-error positive.

- `use_mox.py` imports `mox` and uses only supported keywords; it stays clean.
- Accepted keyword calls in `positive_and_near_misses.py` stay clean.
- `upstream_wrong_arguments.py` includes the decisive upstream test and realistic near misses. Its file header records the GitHub CodeQL source path, pinned commit, and MIT attribution.
