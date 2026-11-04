# Python `print-during-import` fixture

Mirrors CodeQL `python/ql/src/Statements/TopLevelPrint.ql` at commit `ae741615f3e178ce61289a651790dc67fcc18e19`. This rule has no upstream query-test suite; the fixture exercises module-scope builtin calls and the CodeQL main-guard exception.

Validated with Bifrost 0.12.0, build identity `fbad32f32763d2561338f93c61a1523354849a43`, evaluation date `2026-10-08`. The reported policy hash is `2ca1e0710c676a1903a8e56abbcd3a981a39031573f6de24b274bc1f8c07bb7c`; the run is `complete` with 3 findings.

Positive cases: `noisy_module.py:1`, `noisy_module.py:4`, and `noisy_module.py:14`. `main.py` imports the module. Near misses stay clean: the function-body call at `noisy_module.py:8`, and the `if __name__ == "__main__"` call at `noisy_module.py:12`.
