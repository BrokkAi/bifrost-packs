# Python `hashlib.new` constant-dispatch probe

This prototype asks whether Bifrost can discover calls to `hashlib.new` with a
constant algorithm that also has a named constructor. It is research material;
the policy below is discovery-only and is not registered in a pack manifest.

The candidate list follows the canonical named constructors documented by
[CPython](https://docs.python.org/3/library/hashlib.html), excluding `md5`
because some FIPS builds omit or block it. The query matches ordinary quoted
literal spellings only. It covers positional `new("sha256", data)` and
keyword `new(name="sha256", data=data)` forms, keeps other call keywords such
as `usedforsecurity=False` visible, and probes unqualified calls so
`from hashlib import new as alias` is represented. That unqualified probe is
intentionally broad and also selects unrelated callables with the same
constant-argument shape. Dynamic algorithm expressions, provider-specific
names, and noncanonical spellings are excluded. Omitted-data calls are
included: on the recorded runtime, `hashlib.new("sha256")` and
`hashlib.sha256()` return the same empty-input digest.

The local runtime witness compares `hashlib.new` with each named constructor
for the same input and `usedforsecurity=False`. It also checks the `name=` and
`data=` form accepted by `new`, as well as omitted-data equivalence. The named
constructor input is passed positionally because the recorded runtime rejects
`data=` for `sha256`. CPython added `usedforsecurity` to all hashlib
constructors in Python 3.9. This proves only the recorded CPython runtime
behavior. It does not prove the target project's Python version or OpenSSL
provider. CPython documents that named constructors are faster than `new`,
but this probe does not measure performance.

The static result stops before an advisory. With the recorded Bifrost 0.12.0
build, import bindings retain the source path segments `hashlib` and sometimes
`new`, but their boundary is `external_unknown`. A local parameter shadow is
resolved lexically, while an import alias does not establish that the imported
module is CPython's standard library. The pinned Python semantic slice in this
repository contains no `hashlib.pyi`, and its activation begins at CPython
3.10; the local witness runtime is CPython 3.9.6. Constructor availability,
`usedforsecurity` support, and exact module identity therefore remain
unqualified for a consumer project. No performance advisory, severity, or
scanner enablement is claimed.

For a source-only replay, set `BIFROST_012` to the Bifrost 0.12.0 binary whose
SHA-256 is recorded in `outcomes.json`, then run:

```sh
"$BIFROST_012" --root . --query-file queries/constant-new-positional.rql
"$BIFROST_012" --root . --query-file queries/constant-new-keyword.rql
"$BIFROST_012" --root . --query-file queries/constant-new-import-aliases.rql
"$BIFROST_012" --root . --query-file queries/candidate-bindings.rql
"$BIFROST_012" --root . --no-builtin-policies \
  --policy-file rqlp/discovery-only.rqlp \
  --evaluation-date 2026-10-01 --format json
python3 fixtures/runtime-witness.py
```

The source and query files are independently authored public API fixtures.
They do not import or copy implementation from a private repository.
