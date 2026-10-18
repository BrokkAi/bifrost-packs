# CPython runtime-base model preparation

`stdlib-apis/bifrost.python-runtime-bases.json` is prepared by
[`observe-pinned-python-runtime-bases.py`](../../scripts/upstream/public/observe-pinned-python-runtime-bases.py).
The observer selects every actual type export in `vars(builtins)`, plus exactly
`unittest.TestCase` and `unittest.case.TestCase`. It requires those two selected
exports to be the same class object, reads each canonical identity through
`type.__getattribute__` and closes the selected classes over their actual ordered
`__bases__`. It records actual `__mro__` values as observation evidence. It does
not enumerate other unittest classes, inspect workspace or typing classes,
instantiate a test case, or invoke test methods.

The observer requires isolated CPython 3.13.5 with optimization off, bytecode
writes disabled, and executable SHA-256
`889c603f0d17cb54060951bcf4c4f9b8c9ebd9e52b392c70209bbb9755d797d9`.
Before importing either selected module it resolves the actual standard-library
root through `sysconfig` and verifies both selected source files:

| Stdlib-relative file | SHA-256 |
| --- | --- |
| `unittest/__init__.py` | `7c22ee0c503b75aba5221e3e8189f9bf4632f85a43315ff841ec9d26a68e3551` |
| `unittest/case.py` | `ce2499ee6f34a9e6e24f11ae1e2f02e71a3529cca03d5488f0bdcfea8d5d8481` |

The import must select that stdlib package. After import, both actual module
origins, names and source hashes must still match. Preloaded selected modules,
workspace/shadow origins and changed selected source bytes fail observation;
there is no fallback or `sys.path` modification. These are selected-module
source pins, not a hermetic attestation of every transitive stdlib import or
bytecode cache. `-B` suppresses bytecode writes; it does not claim to disable
all existing stdlib bytecode-cache reads.

From the repository root, reproduce the observation with the pinned interpreter:

```sh
python3 -I -B scripts/upstream/public/observe-pinned-python-runtime-bases.py \
  --model-output "$PWD/semantic-packs/python/stdlib-apis/bifrost.python-runtime-bases.json" \
  --observations-output \
  "$PWD/.agents/scratch/python-runtime-bases/observations.json"
```

The command does not download an interpreter. It fails closed when the runtime
or selected module source identities do not match. Model provenance retains the
executable, observer and both selected-module hashes. Raw observations also
record the actual stdlib root and module origins.

The model uses schema 17, exact `=3.13.5` applicability, PSF-2.0 attribution,
`partial` completeness and review-required safety. Its per-class ordered
`runtime_bases` claims do not assert member inventory or complete stdlib coverage.
Stable IDs encode canonical ASCII names in lowercase; names, locator symbols
and qualified aliases preserve Python case. ID collisions are rejected.

The raw observation format is now schema 2: per-class `exports` and the top-level
`exports` mapping contain module-qualified bindings, replacing builtin-only
names. Alias ownership is grouped by actual object identity, never inferred
from a basename. An export identical to its canonical name remains in raw
evidence but is omitted from the model's aliases. Canonical
`unittest.case.TestCase` therefore has alias `unittest.TestCase`, with no duplicate
class identity. This is an observation-format change, not a new product schema.
Records and exports are sorted; canonical JSON has sorted keys and a final
newline. No process object addresses or timestamps are serialized.

Pack and observer-producer versions are `1.1.0`: a compatible source-catalog
addition under the repository's release-versioning guidance. Two fresh isolated
observer executions produced identical model and raw-observation bytes. All 96
previous declaration records, including IDs, aliases and base edges, remain
exactly unchanged. The only additional declaration is
`type.python.unittest.case.testcase`. Independent native observation confirmed
that the two exports name the same class object, its canonical identity is
`unittest.case.TestCase`, its direct base is `builtins.object`, and its actual MRO
is `[unittest.case.TestCase, builtins.object]`. The current source contains 97
classes, 97 ordered direct-base edges and 100 qualified export bindings.

The earlier 1.0.0 full96 model passed bounded compiler and local bundle generation
checks. That acceptance does not qualify this expanded 1.1.0 source. Compilation,
native packaging and runtime consumer qualification of 1.1.0 remain pending.
This source update does not select a release version or generation job, modify
`native-generation.json`, publish artifacts, or enable a scanner model.

Observer SHA-256:
`f2abb5583565494b45c54ab356027f48d046b5916c3073d899e2f9430e4d90c5`.
Model SHA-256:
`e5a8e0218accb4fbe3db597a9152e4ae585b8e66069e46ed57230b04012a93d4`.
Paired raw-observation SHA-256:
`8150066fb6bd05758a4dc5bcb4e20f59a0f71a0116e774312a7b7753a33772b6`.
