# C# too-many-ref-parameters parity fixture

Mirrors CodeQL `csharp/ql/src/Bad Practices/Declarations/TooManyRefParameters.ql`
at commit `ae741615f3e178ce61289a651790dc67fcc18e19`. The upstream test
sources keep their CodeQL paths and an MIT attribution header. The two header
lines shift upstream line numbers by two.

CodeQL counts the parameters of a source method for which `isRef()` holds and
reports a count above two. `isRef()` is parameter mode 1; `out` (2), `in` (5)
and `ref readonly` (6) are separate modes. `Method` excludes constructors,
operators, accessors, delegates and local functions.

The engine contract reports a C# method declaration whose source text holds at
least three `ref` parameter modifiers. Signature parameter rows carry the type
without its modifier, and C# has no structural parameter kind, so the
modifier is read from source. A modifier counts when it follows the opening
parenthesis or a comma, after optional attributes and `this` or `scoped`, and
is not followed by `readonly`. The scan stops at the first `{` or `=`: a `ref`
parameter cannot follow an optional one, so default values, expression bodies
and block bodies never contribute. The structural `method` kind is the method
declaration alone, matching CodeQL's `Method`. No semantic model is installed.

Near misses in `Probe.cs`: two `ref` and one `out`, `in` and `ref readonly`
beside two `ref`, a default value whose string holds `, ref`, an expression
body and a block body that pass three `ref` arguments, a local function, a
constructor, a delegate and an operator. The upstream `Good` class has no
`ref` parameter.

## Validation

Bifrost 0.14.2, build identity `073c23790739e33f33abc98338651689eaf8b7c0`,
evaluation date `2026-10-28`, run from this directory with
`BIFROST_OPEN_PACKS_DISABLE=1`, `--no-builtin-policies` and `--no-incremental`.
The policy hash is
`3f3712338fa273975969be928e3c61732d84571a688e027803777ea13a0fda8c`.

The run is complete with six findings. The upstream expected row is
`TooManyRefParametersBad.cs:7` (`PopulateDetails`, upstream line 5). The five
probe positives are `Probe.cs:7` (`Normalize`), `:9` (generic `Swap3<T>` with
a constraint), `:11` (`Shift`, with `this ref` and `scoped ref`), `:13`
(`Merge`, parameters on separate lines with attributes and a type named
`readonlyCounter`) and `:46` (`IAccumulator.Accumulate`, with no body). There
are no other findings.

## Known limits

- A comment inside the parameter list can add or hide a `ref` token.
- An attribute with a named argument, as in `[Foo(Name = "x")]`, stops the
  scan at its `=`, so later `ref` parameters are not counted.
- `this ref` is counted as `ref`. I have not checked whether CodeQL's
  extractor records an extension receiver passed by reference as mode 1.
- Each part of a partial method is matched separately. I have not checked
  how CodeQL counts the pair.
- The finding names no parameter count, unlike CodeQL's message.
