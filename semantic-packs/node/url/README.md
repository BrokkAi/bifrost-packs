# Node `url` packs

These public packs give the reviewed JavaScript Node core legacy `url.parse`
and `url.format` members. The
`bifrost.security.javascript.process-input-to-legacy-url-parse` policy
(BrokkAi/bifrost-packs#294) uses them as exact sinks.

The model provenance is Node.js `v22.11.0`. The JSON packs are authored Bifrost
semantic facts under the repository's `Apache-2.0` model license. They require
reviewed activation (`safety.review_required: true`) and use the same Node
`22.11.0` activation selector as the `fs` packs. The Node distribution notice
is at `semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.

## Reviewed claims

The claims rest on `doc/api/url.md` at Node `v22.11.0` (SHA-256
`edb9856bf9176279c9b8d2060959256f101fe5e4344daea95c750ed408b64ce7`,
`https://github.com/nodejs/node/blob/v22.11.0/doc/api/url.md`):

- `url.parse(urlString)` returns a URL object built from the string, so the
  argument flows to the normal return. The documentation says the legacy
  parser is prone to host name spoofing and must not be used with untrusted
  input.
- `url.format(urlObject)` returns a string built from its argument, and a
  string argument is first passed to `url.parse()`. The argument flows to the
  normal return.
- Both members can throw on invalid input, so the argument also flows to the
  exceptional return.
- The namespace receiver flows to itself, and each summary claims every
  outside-workspace implementation of its member (`covers_overrides`).

## Scope

Only the one-argument forms are modeled. `url.parse` with
`parseQueryString` or `slashesDenoteHost`, and `url.format(URL, options)`,
don't bind and stay fail-closed. The returned `Url` object has no property
model, so reading `.hostname` from it leaves a run inconclusive. The WHATWG
`URL` class, `url.fileURLToPath` and `url.pathToFileURL` are not modeled.
