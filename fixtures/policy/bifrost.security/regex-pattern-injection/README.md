# C# regular-expression pattern injection fixture

Qualifies the version-independent part of the .NET CVE lead
BrokkAi/bifrost-packs#263 (CVE-2019-0820, GHSA-cmhx-cq75-c4mj). A pattern the
caller writes can backtrack catastrophically on every runtime unless a match
timeout bounds it. So external input reaching the pattern operand of a `Regex`
constructor or static `Regex` method with no `matchTimeout` argument is
reported on every version. The CVE's affected-package range (4.3.0) is not
checked.

The sources are `Console.ReadLine` and `Environment.GetEnvironmentVariable`
from `bifrost.dotnet.bcl-csharp` 0.4.0. The sinks bind to the reviewed
`bifrost.dotnet.system-text-regularexpressions-csharp` 0.1.0 model in
`.bifrost/semantic-models`, and `model_id` narrows each one to the overload
with no `matchTimeout`:

- `Regex(String)` and `Regex(String, RegexOptions)`;
- static `IsMatch`, `Match`, `Matches` and `Split` with `(input, pattern)` and
  `(input, pattern, options)`;
- static `Replace` with `(input, pattern, replacement)` and
  `(input, pattern, replacement, options)`.

`Regex.Escape` removes the untrusted label. The model also declares every
`matchTimeout` overload, so those calls bind to their own members and stay near
misses. It declares no instance `Regex` method: on Bifrost 0.15.1 an instance
overload in the same family makes the static locator ambiguous
(bifrost-dev#9982).

## Cases

- **Positives** (`Probe.cs`): both constructors, `IsMatch` directly and through
  a `var` local, `Match`, `Matches`, `Split`, and both `Replace` overloads.
- **Near misses** (`Probe.cs`): an escaped pattern, untrusted input text with a
  constant pattern, an untrusted replacement with a constant pattern,
  `IsMatch`, `Replace` and the constructor with a `matchTimeout`, and a
  same-named `Local.Regex.IsMatch`.
- **Incomplete** (`incomplete/`, one directory per case). `.bifrostignore`
  keeps this workspace out of the parent run.
  - `typedlocal`: `string pattern = Console.ReadLine();`. A call that
    initializes an explicitly typed local has unknown call resolution
    (bifrost-dev#8299 item 3). A `var` local works.
  - `field`: the pattern comes from a field initializer. The source selector
    is partial and binds no source (bifrost-dev#8299).
  - `matchsuccess`: `Regex.Match(...).Success`. The finding is reported, but
    access-path resolution for the member read is unknown.
  - `evaluator`: `Regex.Replace(text, pattern, m => "*")`. The finding is
    reported, but the lambda's procedure semantics are unknown. The model has
    no `MatchEvaluator` overload, and the call binds to the `String
    replacement` overload anyway (bifrost-dev#9981).

## Validation

Bifrost 0.15.1 (`bifrost-v0.15.1-aarch64-apple-darwin.tar.gz`, archive SHA-256
`4dd3c31a47477581610f35ca1a588d7cce50d500ed9fcf5967f1240766483a8c`, which
matches the release digest; binary SHA-256
`78a4c1754a4c8468c082edb9cf56ae370f9c61be47c54b302e5ded30e4fe3b33`; build
identity `90d820b9ee3b1bcca9e3dd2a049b1b51dc854b69`), evaluation date
`2026-11-05`. Each run used `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `--no-builtin-policies`,
`--no-incremental` and a fresh `BIFROST_CACHE_DIR`. The authored policy hash
is `a49111555098e3a0d31fbaae6c8889d3055204ba9f5833b808b22c15036effc3`. Its
resolved identity is workspace-required.

- This directory: `proven_by_summary`, with 9 findings, all definite and
  complete: `Probe.cs:10`, `:16`, `:22`, `:28`, `:33`, `:38`, `:43`, `:48` and
  `:53`. The near misses produce no finding and no diagnostic.
- `incomplete/`: inconclusive (`partial_discovery`). Each case was also run
  alone with `--sources <case>`, and each is inconclusive on its own.
- Without the System.Text.RegularExpressions model: `not_run`.

## Known limits

- Only console and environment input are sources. Request input has no
  selectable C# source yet (bifrost-dev#8307).
- Instance calls such as `regex.IsMatch(text)` are unmodeled. A constructor
  with an untrusted pattern is still reported at the constructor.
- The `ReadOnlySpan<char>` overloads, `Count`, `EnumerateMatches` and the
  `MatchEvaluator` overloads of `Replace` are not declared. Same-arity
  overloads that differ by parameter type don't bind on 0.15.1
  (bifrost-dev#8296).
- An app-wide default timeout (`REGEX_DEFAULT_MATCH_TIMEOUT` in `AppContext`)
  is not visible, so code that relies on one is still reported.
- `[GeneratedRegex]` source-generated patterns are constants and are not
  reported.
