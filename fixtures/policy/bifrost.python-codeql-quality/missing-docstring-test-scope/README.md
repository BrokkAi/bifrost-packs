# Python `missing-docstring` test-code and entry-point fixture

`missing-docstring` does not report test code or script entry points
(bifrost-dev#11358). Adding a test file or a small script must not fail a
default check because its test classes, test functions or `main()` lack
docstrings. The upstream CodeQL query is recommendation-level and has no such
exclusion, so this is a deliberate departure from CodeQL parity.

The engine classifies both structurally on each `python-documentation` row:

- `test_scope` is `yes` for every declaration in a module pytest collects by
  default (`test_*.py`, `*_test.py`) or in `conftest.py`, inside a class whose
  bases include `unittest.TestCase` (also through `from unittest import
  TestCase as Base`), and for a `test*` function in a module that imports
  pytest or nose. It is `unknown` when an enclosing class hierarchy does not
  resolve completely.
- `entry_point` is `yes` for a module-level function that a call inside the
  module's top-level `if __name__ == "__main__":` block resolves to, such as
  `sys.exit(main())`. It is `unknown` when a same-named call there does not
  resolve.

The policy reports only rows where both are `no`. An `unknown` row is not
reported and leaves the run incomplete with a `row_predicate_undecided`
diagnostic.

Expected findings:

- `library.py`: the module, `Widget`, `Widget.resize`, and `main` (not called
  from a `__main__` block).
- `tool.py`: the module and `report`. `main` is an entry point.
- `checks.py`: the module and `build_marker`. `Checks` and `test_marker` are
  test code.
- `derived.py`: the module. `DerivedChecks` extends a workspace TestCase
  subclass; without a stdlib pack the hierarchy stays incomplete, so its
  test scope is `unknown` and it is withheld.

Not reported: everything in `test_example.py`, `widgets_test.py` and
`conftest.py`.
