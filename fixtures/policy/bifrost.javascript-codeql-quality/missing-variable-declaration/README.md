# JavaScript missing-variable-declaration parity fixture

The ordinary JavaScript and TypeScript assignments are proven findings. The
`dynamic.js` near-miss deliberately exercises `with` and direct `eval`; those
constructs make binding/liveness coverage incomplete, so the qualification
run reports the proven findings with an inconclusive completion rather than
claiming a clean result.
