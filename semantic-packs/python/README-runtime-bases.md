# CPython runtime-base model preparation

`stdlib-apis/bifrost.python-runtime-bases.json` is prepared by
[`observe-pinned-python-runtime-bases.py`](../../scripts/upstream/public/observe-pinned-python-runtime-bases.py).
The observer selects every actual type export in `vars(builtins)`, plus exactly
`unittest.TestCase`, `unittest.case.TestCase`,
`collections.abc.MutableMapping`, `_collections_abc.MutableMapping` and
`threading.Thread`. It requires both TestCase exports to name one class object
and both MutableMapping exports to name one class object. It reads each
canonical identity through `type.__getattribute__` and closes the selected
classes over their actual ordered `__bases__`, recording actual `__mro__`
values as observation evidence. It does not enumerate other module classes,
inspect workspace or typing classes, instantiate a thread or test case, or
invoke their methods.

The observer requires isolated CPython 3.13.5 with optimization off, bytecode
writes disabled, and executable SHA-256
`889c603f0d17cb54060951bcf4c4f9b8c9ebd9e52b392c70209bbb9755d797d9`.
The selected file pins are:

| Stdlib-relative file | Role | SHA-256 |
| --- | --- | --- |
| `unittest/__init__.py` | Fresh selected module | `7c22ee0c503b75aba5221e3e8189f9bf4632f85a43315ff841ec9d26a68e3551` |
| `unittest/case.py` | Fresh selected module | `ce2499ee6f34a9e6e24f11ae1e2f02e71a3529cca03d5488f0bdcfea8d5d8481` |
| `threading.py` | Fresh selected module | `61e1cd79adb93cfacf69dc3900ea99fbc8042d65f3742233c07c5707e39add84` |
| `_collections_abc.py` | Retained companion file | `2cfe340c4cf54077f054cd366a2c7a515e9ee8da7d8b3fa071251f280034756d` |
| `collections/__init__.py` | Retained companion file | `2347f647577b6c11b82fc48fa4a1744f7af1af87f15942f92b7cc4410f0a817b` |

## Fresh and frozen module identities

Threading and both unittest modules must be absent before source verification.
On this interpreter, importing `sysconfig` itself imports `threading`. The
observer therefore first pins the fresh source files under CPython's runtime
`sys._stdlib_dir`, then imports `sysconfig` and requires its actual stdlib root
to agree. Before selecting classes it verifies actual module names, import
specifications, module bindings, source origins and hashes again. Preloaded
fresh modules or workspace/shadow origins fail observation; there is no
fallback or `sys.path` modification.

The ABC modules have a separate contract: the actual runtime preloads
`collections.abc` and `_collections_abc`, and the observer accepts and records
that fact. Both bindings and `collections.abc` on the parent package must name
the same module object, with the same MutableMapping class object. The module's
actual name is `collections.abc`, its spec name is `_collections_abc`, its origin
is `frozen`, and its loader must be the actual `FrozenImporter` object. The
observer verifies these identities and spec/module bindings. It retains the
actual preloaded state, module names, spec names, loader and file origins.

The two companion files are hash-pinned before ABC inspection and checked
again afterward. These files are not asserted to be the executed frozen code;
there is no `collections/abc.py` input. Executable identity and actual class
inspection remain the primary observation. Selected source and companion pins
are not a hermetic attestation of all transitive stdlib imports. `-B` suppresses
bytecode writes; it does not disable all existing bytecode-cache reads.

From the repository root, reproduce the observation with the pinned interpreter:

```sh
python3 -I -B scripts/upstream/public/observe-pinned-python-runtime-bases.py \
  --model-output "$PWD/semantic-packs/python/stdlib-apis/bifrost.python-runtime-bases.json" \
  --observations-output \
  "$PWD/.agents/scratch/python-runtime-bases/observations.json"
```

The command does not download an interpreter. It fails closed when runtime,
selected-module or companion identities do not match. Model provenance retains
the executable, observer and selected file hashes with their distinct roles;
raw observations also retain actual stdlib root and module identity evidence.

The model retains schema 17, exact `=3.13.5` applicability, PSF-2.0 attribution,
`partial` completeness and review-required safety. Per-class ordered
`runtime_bases` claims do not assert member inventory or complete stdlib coverage.
Stable IDs encode canonical ASCII names in lowercase; names, locator symbols
and qualified aliases preserve Python case. ID collisions are rejected.

Raw observation schema 3 adds the explicit frozen-module identity and companion
file contract. Per-class `exports` and the top-level `exports` mapping retain
module-qualified bindings. Alias ownership follows actual object identity;
export names come from the requested module binding, never blindly from
`module.__name__`, because the ABC bindings intentionally share a module.
Canonical exports remain in raw evidence but are omitted from model aliases.
Thus `collections.abc.MutableMapping` has alias
`_collections_abc.MutableMapping`, while canonical `unittest.case.TestCase`
retains `unittest.TestCase`. Records and exports are sorted; canonical JSON has
sorted keys and a final newline. No addresses or timestamps are serialized.

## Bounded validation and delivery status

Pack and observer-producer versions are `1.2.0`, a compatible source-catalog
addition under the repository's release-versioning guidance. Two isolated
observer runs produced identical model and raw bytes. All 97 prior declaration
records, including IDs, aliases and ordered base edges, remain exactly unchanged.
Only actual required base closure is added: `collections.abc.MutableMapping`,
`Mapping`, `Collection`, `Sized`, `Iterable`, `Container`, and `threading.Thread`.
An independent native check verified the public/private identities, actual
ordered bases and MROs, unchanged prior records, and absence of extra classes.
The source now has 104 classes, 106 ordered base edges and 103 export bindings.

The 1.2.0 source passed local native-bundle generation and integrity verification:
all 104 class records agree with the authored model, all 97 prior compiled
records remain exactly unchanged, and there are no rejected or suppressed
records. The same seven-class consumer probe resolved all three MutableMapping
import forms and both Thread import forms to their canonical classes with
complete, ordered ancestry claims; the TestCase and dict controls remained
complete. These checks used the admitted Bifrost consumer at
`ba7a692dbd0b8a02d0d6e68ca03f823d9c5b52e7`.

One unchanged full-repository Bottle replay qualified all three native variants
and selected the local 1.2.0 pack in all six cold/warm policy requests. Compared
with the corresponding 1.1.0 requests, each diagnostic set fell from 11 to 6:
the same five roots were removed, the same six were retained, and none was
added. Full retained diagnostic records were unchanged, with no diagnostic
truncation. Observed scoped counts remained 0/1/0 in both modes, but all six
requests were incomplete and none was scorable. This is bounded bundle and
consumer evidence, not whole-repository Bottle policy qualification.

The native bundle remains local and unpublished.

This source update does not select a release version or generation job, modify
`native-generation.json`, publish artifacts, or enable a scanner model by default.

Observer SHA-256:
`64c5558ecbf09037e92cdb779d093ae357f48730bdafe6d70f517b70e700fc02`.
Model SHA-256:
`09dcf611a1c613fec2f772722fd073cce961d819a8c6231dc2277cf3a106609c`.
Paired raw-observation SHA-256:
`5e87b0c8ec226b34744f0273b4dc11df176adb00ed4e916800fdc74ddf394686`.
