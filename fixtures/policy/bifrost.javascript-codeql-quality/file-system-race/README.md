# JavaScript file-system-race fixture

This fixture installs the public reviewed Node `fs` declaration and summary
packs from `semantic-packs/node/fs/javascript/` through `.bifrost/packs.json`.
The models record Node.js `v22.11.0` provenance, use the repository's
`Apache-2.0` model license, and remain explicitly review-required and partial.

`main.js` contains two same-path check/use positives and near misses for an
unrelated path and a safe read. `reassigned.js` retains the engine golden's
path-rebinding case; the engine reports the two proven findings while marking
the assertion incomplete when that binding cannot be resolved completely.
