# CPython runtime-base model preparation

`stdlib-apis/bifrost.python-runtime-bases.json` is prepared by
[`observe-pinned-python-runtime-bases.py`](../../scripts/upstream/public/observe-pinned-python-runtime-bases.py).
The observer reads only the active interpreter's `vars(builtins)` and actual
class `__bases__`/`__mro__` objects. It does not import or execute workspace
projects, infer ancestry from names, or include classes discovered through
`typing`.

The observer refuses to run unless it is CPython 3.13.5, optimization is off,
and the executable SHA-256 is
`889c603f0d17cb54060951bcf4c4f9b8c9ebd9e52b392c70209bbb9755d797d9`. The model
records the interpreter and observer hashes in the existing provenance strings.
The separate raw-observation file preserves each selected class's canonical
runtime name, builtin aliases, ordered direct bases, and runtime MRO. It records
object identity by grouping actual aliases, without serializing process memory
addresses. In the authored model, each alias is emitted as the qualified name
`builtins.<observed binding>` from the actual `vars(builtins)` entry, excluding
an alias identical to the class's canonical name. Alias ownership is never
inferred from the class basename. The raw observation keeps the original
unqualified binding names and all observed bases/MRO unchanged.

From the repository root, reproduce the observation with the pinned interpreter:

```sh
python3 -I -B scripts/upstream/public/observe-pinned-python-runtime-bases.py \
  --model-output "$PWD/semantic-packs/python/stdlib-apis/bifrost.python-runtime-bases.json" \
  --observations-output \
  "$PWD/.agents/scratch/python-runtime-bases/observations.json"
```

`-I -B` isolates Python startup and suppresses bytecode writes; the observer
independently checks the executable hash, version, and optimization setting.
The command does not download an interpreter or depend on a particular host
path. It fails closed if the active `python3` does not match the pinned binary.
The model draft uses schema 17, exact `=3.13.5` applicability, PSF-2.0
attribution, and `partial` completeness. Its per-class ordered
`runtime_bases` claims do not assert member inventory completeness.

The authored JSON is preparation content. Native generation/release selection
is separate; this README does not add the model to `native-generation.json` or
select a release version. The current release recipe's pinned native
producer predates schema 17 support. Runtime consumer qualification and review
of the authored-model spec remain prerequisites for native release selection.

Stable model IDs encode the observed ASCII canonical name in lowercase, while
class names, aliases and locator symbols preserve Python's case-sensitive
spelling. The observer checks the shared identifier grammar and length and
rejects ID collisions before writing either output. Definitions and declared
base references use the same canonical-name-to-ID map.

After the ID correction, one fresh isolated execution produced the current
model and observations. A file comparison with the earlier observation found
identical runtime classes, ordered bases, MROs and aliases; only the actual
observer hash changed in the raw evidence. Model records changed only their
IDs and declared references, with the new observer hash retained in provenance.
All 96 IDs are unique and every base reference belongs to that set. The model
contains 96 classes, 96 ordered base edges and 98 builtin bindings. These checks
establish observation and derivation consistency, not semantic compiler or
engine consumer acceptance.

Corrected observer SHA-256:
`11e34218fd9650a138b48ea1b8c887ce36d260fae01acfc8db6cdf6734b8b979`. The
reviewed model SHA-256 is
`31374ef33b33e8640eb89a309a852404ed088d2ab37af0fd6cac1c056715b240`; its paired
raw-observation SHA-256 is
`7a7e8dd21b40960d4e7f3cf433b425d0f60fbc92c6f0c342ed21716dc7d7a643`.

A source-pinned schema-17 compiler accepted this exact full model and emitted
one declaration shard containing all 96 class records. This establishes format
and artifact-generation acceptance only. Runtime consumer qualification and
native release selection remain pending.
