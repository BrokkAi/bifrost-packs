# Python untrusted-input parsing packs

These two packs back the opt-in policies
`bifrost.security.python.flask-request-to-parse-qs` (lead
BrokkAi/bifrost-packs#436) and
`bifrost.security.python.flask-request-to-decompress` (lead #435). They are
hand-reviewed against the pinned typeshed revision
`1620e225476597f34177351ef913dc8390dade30` and CPython 3.13.5. No generator
exists for them.

| Pack | Version | Activates on | Kind |
| --- | --- | --- | --- |
| `bifrost.python-untrusted-parsing-declarations` | 0.1.0 | toolchain `cpython` `>=3.10.0, <3.15.0` | declarations |
| `bifrost.python-untrusted-parsing-summaries` | 0.1.0 | toolchain `cpython` `>=3.13.5, <3.13.6` | procedure summaries |

They are separate from `bifrost.python-stdlib-api-declarations` and
`bifrost.python-security-sink-summaries` so that they can ship without a version
bump of those packs. They are source-only: `native-generation.json` does not
build them, so no packs release delivers them yet, and both policies stay
opt-in until one does. The declaration pack repeats the module record
`type.python.urllib.parse` of the stdlib API pack, because a pack must declare
the owner of each member it declares. The two records are identical, and the
fixtures load both packs together.

## Reviewed claims

Declarations (`urllib/parse.pyi`):

- `urllib.parse.parse_qs(qs, keep_blank_values, strict_parsing, encoding,
  errors, max_num_fields, separator)` and `parse_qsl` with the same formals.
  Only `qs` is required. `max_num_fields` is the sixth formal and may be passed
  positionally. The stdlib API pack declares only `urlparse` in this module, and
  the typeshed pack does not cover `urllib.parse`, so `parse_qs` had no exact
  identity before this pack.

Summaries (all complete, no effects):

- `urllib.parse.parse_qs` and `parse_qsl`: `qs` flows to the return value, and
  to the exceptional return, because with `strict_parsing=True` a malformed
  field raises a `ValueError` whose message quotes that field.
- `zlib.decompress(data, /, wbits, bufsize)` (`zlib.pyi`), `gzip.decompress(data)`
  (`gzip.pyi`) and `bz2.decompress(data)` (`bz2.pyi`): `data` flows to the return
  value. The typeshed pack declares these functions; the summaries close them.
  None of them takes an output bound.
- `base64.b64decode(s, altchars, validate)`, `standard_b64decode(s)` and
  `urlsafe_b64decode(s)` (`base64.pyi`, the `sys.version_info < (3, 15)`
  branch): `s` flows to the return value. The summary pack activates only on
  CPython 3.13.5, so the 3.15 `padded` and `ignorechars` keywords are out of
  scope.

## Not modeled

- `zlib.decompressobj()` and `zlib._Decompress.decompress(data, max_length)`.
  A declaration with the exact return class `zlib._Decompress` was tried; on
  Bifrost 0.15.4 the receiver of `decompressobj().decompress(...)` still does
  not dispatch exactly, so the streaming form is left out rather than declared
  without evidence.
- `lzma.decompress`: the typeshed pack does not cover `lzma`.
- `str.encode`: a receiver read from `headers.get(...)` is `str | None`, and
  the call does not dispatch exactly on 0.15.4.
