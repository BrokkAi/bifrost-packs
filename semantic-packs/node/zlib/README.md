# Node `zlib` packs

`bifrost.node-zlib-javascript-declarations` 0.1.0 and
`bifrost.node-zlib-javascript-summaries` 0.1.0 are source-only packs for the
JavaScript Node core `zlib` convenience methods that decompress a whole buffer
at once. They back the `file-content-to-unbounded-decompression` security
policy, the version-independent part of BrokkAi/bifrost-packs#291
(CVE-2024-22025).

## Declarations

For each of `gunzipSync`, `inflateSync`, `inflateRawSync`, `unzipSync` and
`brotliDecompressSync`, the declarations pack has two members: the
one-argument `zlib.<name>(buffer)` and the two-argument
`zlib.<name>(buffer, options)`. The one-argument form returns a `Buffer`. The
two-argument form returns `any`: with `info: true` the result is an object
holding `buffer` and `engine`.

The source is `doc/api/zlib.md` at Node `v22.11.0` (SHA-256
`9ec5e920cb53e58b84d0b74836c1cb995fe5f6dce9079daf77b860ed5b3e956a`, from
`https://github.com/nodejs/node/blob/v22.11.0/doc/api/zlib.md`). It documents
each method as `zlib.<name>(buffer[, options])`. It also documents
`maxOutputLength`, the option that limits the output size of these convenience
methods, with a default of `buffer.kMaxLength`. A call without options
therefore has no output limit beyond the largest `Buffer` the process can
allocate. The policy uses only the one-argument members as sinks.

## Summaries

Each summary is complete and covers one declared member:

- The namespace receiver flows to itself.
- The `buffer` argument flows to the normal return. The result is the
  decompressed form of the input, so data chosen by whoever wrote the input
  stays in it.
- In the two-argument form, `options` also flows to the normal return. A
  `dictionary` supplies bytes of the inflated output, and `info: true` returns
  an object that holds the result.
- Every argument flows to the exceptional return. A failed call throws an
  error, and a may-analysis must not assume that the error drops its inputs.
- There are no effects. The methods only compute a new buffer.

## Not modeled

The callback forms (`zlib.gunzip(buffer, callback)` and the others), the
stream classes (`createGunzip` and the others), the compression methods, and
the `options` fields. Because option shapes don't bind, a two-argument call is
never a sink, even when its options omit `maxOutputLength`.

The packs carry the repository's `Apache-2.0` model license and set
`safety.review_required: false`. They are source-only: no native release
recipe includes them yet. The Node distribution notice is retained at
`semantic-packs/node/runtime-values/notices/node-v22.11.0.txt`.
