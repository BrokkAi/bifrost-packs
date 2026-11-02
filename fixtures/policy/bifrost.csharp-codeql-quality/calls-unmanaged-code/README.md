# C# calls-unmanaged-code parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/CallsUnmanagedCode.ql` at commit
`ae741615f3e178ce61289a651790dc67fcc18e19`. CodeQL has no query test for it
at that commit; the qhelp example keeps its CodeQL path and an MIT
attribution header. The two header lines shift upstream line numbers by two.

CodeQL reports a `MethodCall` whose target is an `extern` method declared in a
`Class`. `Method` excludes local functions, constructors, operators and
accessors; `Class` excludes structs and interfaces.

The engine contract reports proven calls whose exact target is a C# `method`
declaration with the `extern` modifier, unless the method lies inside a struct
or interface. C# has no structural modifier fact, so the modifier is read from
the declaration header: after optional attribute lists and before the first
`(`, `{`, `;` or `=`. A string or body that contains `extern` does not count.
No semantic model is installed.

Near misses in `Probe.cs`: a managed method with the same signature, a method
whose body holds the text `extern`, a `DllImport` method declared in a struct,
and an `extern` local function.

## Validation

Bifrost 0.15.0, build identity `09a2503c5f7ced1630a9e3c445ead53dfc5925e8`,
evaluation date `2026-11-02`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The authored policy hash is
`a38ffa41d2e363e4d5b3a46a25545d1ec99ebc3a278666c0200cc9dee10c6736`; its
resolved identity is available and equal.

The run is complete with four findings. The upstream expected row is
`CallsUnmanagedCode.cs:14` (upstream line 12). The three probe positives are
`Probe.cs:49` (`DllImport` with named arguments), `:50` (two attribute lists,
one with a `return:` target) and `:51` (an instance `MethodImplOptions.InternalCall`
method). There are no other findings.

## Known limits

- A call qualified by a constructed generic type, as in
  `Native<int>.GetLastError()`, is unproven. The engine drops it without a
  diagnostic, so the run reports complete without the finding.
- A call qualified by a nested type, as in `Outer.Inner.Sleep(1)`, is
  unproven; the run is inconclusive.
- A method group that names an `extern` method, as in
  `Func<int> f = Native.GetTickCount;`, makes the run inconclusive. CodeQL does
  not report it, because it is not a call.
- `inside` is transitive, so an `extern` method in a class nested in a struct
  is excluded. CodeQL reports it.
- A `]` inside an attribute string, or a comment with `(`, `{`, `;` or `=`
  between the attributes and the modifier, hides the modifier.
- The message does not name the target, unlike CodeQL's alert location text.
