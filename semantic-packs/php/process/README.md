# PHP process summaries

`bifrost.php-process-summaries` 0.1.0 is a source-only pack with reviewed
procedure summaries for the PHP builtin `proc_open`, used by the
`request-input-to-proc-open-command` security policy (BrokkAi/bifrost-packs#311).
The `proc_open` declaration itself comes from the `bifrost.php-builtin` native
pack, which is generated from the pinned phpstorm-stubs slice; that pack has no
summaries.

## Reviewed claims

Each summary targets the receiverless `proc_open` declaration in
`standard/standard_2.php`, with 3, 4, 5 or 6 arguments
(`command`, `descriptor_spec`, `&pipes`, `cwd`, `env_vars`, `options`). The
claims follow the PHP manual page for `proc_open`:

- The call returns one value, a process resource or `false`. No argument flows
  into it, so the summary has no transfers.
- The command argument escapes to the `php.proc-open.command` event: the
  function starts that command. A string runs through the system shell, and an
  array runs the program directly with its elements as arguments.

## The `$pipes` argument

`proc_open` writes fresh pipe resources into the by-reference `$pipes`
argument. No argument value flows into them, so a summary with no transfer is
accurate for value flow. The summary does not record that the call overwrites
whatever `$pipes` held before; that can only keep a stale value, which errs
toward a false positive, never a false clean. Output the child process writes
reaches PHP only through a later read call on a pipe resource, such as
`fread` or `stream_get_contents`, and that call's own model decides whether
its result is tainted. This pack does not model those reads.

The pack carries the repository's `Apache-2.0` model license and sets
`safety.review_required: false`. It is source-only: no native release recipe
includes it yet.
