# Python predictable path in the shared temporary directory

Fixture for `bifrost.security.python.predictable-temporary-path` (CWE-377),
lead BrokkAi/bifrost-packs#443 (requests CVE-2026-25645). The subject is an
exact `tempfile.gettempdir()` call that is the first of two arguments to a call
spelled `join` whose second argument is a string literal that
interpolates no name. No workspace models are needed: `tempfile.gettempdir` is
declared only by the typeshed stdlib pack in the open bundle.

## Validation

Released Bifrost 0.15.4 (`bifrost-v0.15.4-aarch64-apple-darwin`, build identity
`ea8da845e8d702206a9acc0c6f28d8bd18fa71c0`), evaluation date `2026-11-25`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off`, `BIFROST_OPEN_SEMANTIC_PACK_BUNDLE` set to
the extracted `bifrost-semantic-packs` directory of `packs/v0.16.0`, and a fresh
home and `BIFROST_CACHE_DIR` for each run. Two runs gave the same result.

Result: **complete**, 3 definite findings.

- **Positives** (`main.py`): line 11 (the requests CA-bundle shape: a fixed
  name, reused when it exists), line 20 (`gettempdir` imported with `from`) and
  line 25 (a fixed pid-file name).
- **Near misses** (no finding): a `uuid4().hex` name (line 30), f-strings that
  interpolate a `uuid4()` call (line 35) or a random token held in a local
  (line 41), a fixed name under a random subdirectory (three arguments,
  line 51), the bare directory (line 56), `tempfile.mkstemp` (line 61) and a
  fixed name under a private directory (line 68).
- **Not examined**: an f-string that interpolates a caller-supplied name
  (line 46). The name may be predictable, but the rule cannot tell it apart
  from a random token, so it reports neither.

Run from this fixture directory:

```console
bifrost --root . --policy-file .bifrost/policies/predictable-temporary-path.rqlp --no-builtin-policies --no-incremental --format json --evaluation-date 2026-11-25
```

## Known limits

- `pathlib.Path(tempfile.gettempdir()) / "name"` and string concatenation are
  not matched; only a two-argument `join` call is.
- `join` is matched by spelling: `os.path.join` and `posixpath.join` do not bind
  to an exact identity on 0.15.4.
- A name read from a variable, or interpolated into an f-string, is not
  examined, so a constant held in a local or
  module variable is missed. The requests pre-image builds the name from a zip
  member (`member.split("/")[-1]`) and is therefore missed too; it needs value
  flow from a predictable-name source to `join`.
- The rule does not check whether the path is later reused after an `exists`
  check or opened without `O_EXCL`; a fixed name in the shared directory is
  reported on its own. Even `open(path, "x")`, which refuses an existing file,
  lets another local user block the program by creating the path first.
