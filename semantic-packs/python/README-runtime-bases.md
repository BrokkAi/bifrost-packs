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
addresses.

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
select a release version. The current pinned native producer predates schema
17 support. The engine carrier and reader must land and validate the model
before native release compilation can consume this exact generated source with
its reviewed authored-model spec.

Two isolated executions produced byte-identical model and raw-observation files.
The model contains 96 classes and 96 ordered base edges, with 98 builtin
bindings including aliases. An independent calculation over the retained model
graph reproduced all 96 observed MROs. This establishes the retained graph
correspondence; it is not execution of analyzed projects or two independent
interpreter implementations. Alias bindings remain recorded observations, not a
claim that an engine consumer already resolves every alias. Native schema-17
compiler and consumer qualification are still pending.
