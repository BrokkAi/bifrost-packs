# call-wrong-named-class-argument

Mirrors CodeQL `py/call/wrong-named-class-argument` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`.

Validated with Bifrost 0.13.1, build identity 1cca9d2547b617630111c98c2d09ca01e75cd16a, engine commit bd18ba65413a14dca6d36a145cc6b11fccc57c6f. Policy hash: `8145af5818252df7b80abb44b1d7b82d98869ff65e0930aa49aed48b8e57c2f1`.

## Upstream gate

- Expected: 4; found: 4; abstained: 0; false positives: 0.
- Expected upstream finding lines: `upstream_wrong_arguments.py:67` (upstream line 65), `upstream_wrong_arguments.py:68` (upstream line 66), `upstream_wrong_arguments.py:69` (upstream line 67), `upstream_wrong_arguments.py:94` (upstream line 92).
- True positives beyond CodeQL: none among upstream cases; the authored local positive is a synthetic regression case.
- Abstentions: none. The top-level run includes general analysis-incomplete diagnostics, but every expected upstream row is present.

## Fixture cases

`positive_and_near_misses.py:5` is the authored keyword-error positive. `positive_and_near_misses.py:15` is an additional constructor keyword-error positive.

- `use_mox.py` imports `mox` and uses only supported keywords; it stays clean.
- Accepted keyword calls in `positive_and_near_misses.py` stay clean.
- `upstream_wrong_arguments.py` includes the decisive upstream test and realistic near misses. Its file header records the GitHub CodeQL source path, pinned commit, and MIT attribution.
