# Python standard-library semantic packs

This directory pins the source inputs used to build Bifrost's published Python
standard-library declaration and reviewed assertion packs. Generated manifests
and shards are release assets; they are not checked into Git.

The pinned-spec schema is ecosystem neutral and is documented in
`semantic-packs/jvm/README.md`. This directory adds the first `python_stub`
specification: an exact source set of `.pyi` files taken from one pinned
typeshed revision.

## The pinned slice

`typeshed-stdlib-2026.8.31.json` pins typeshed revision
`1620e225476597f34177351ef913dc8390dade30` and contains 63 explicitly selected
root stubs plus the 149 standard-library modules in their transitive import
closure (212 stubs total). The root set is deliberately bounded to common
runtime and standard-library surfaces.

### Explicit root stubs

| Root module | Pinned stub file |
| --- | --- |
| `_collections_abc` | `_collections_abc.pyi` |
| `_sitebuiltins` | `_sitebuiltins.pyi` |
| `abc` | `abc.pyi` |
| `builtins` | `builtins.pyi` |
| `codecs` | `codecs.pyi` |
| `collections` | `collections/__init__.pyi` |
| `collections.abc` | `collections/abc.pyi` |
| `contextlib` | `contextlib.pyi` |
| `ctypes` | `ctypes/__init__.pyi` |
| `ctypes.wintypes` | `ctypes/wintypes.pyi` |
| `dataclasses` | `dataclasses.pyi` |
| `enum` | `enum.pyi` |
| `errno` | `errno.pyi` |
| `functools` | `functools.pyi` |
| `gettext` | `gettext.pyi` |
| `hashlib` | `hashlib.pyi` |
| `hmac` | `hmac.pyi` |
| `importlib` | `importlib/__init__.pyi` |
| `importlib.metadata` | `importlib/metadata/__init__.pyi` |
| `inspect` | `inspect.pyi` |
| `io` | `io.pyi` |
| `itertools` | `itertools.pyi` |
| `json` | `json/__init__.pyi` |
| `json.decoder` | `json/decoder.pyi` |
| `json.encoder` | `json/encoder.pyi` |
| `json.scanner` | `json/scanner.pyi` |
| `json.tool` | `json/tool.pyi` |
| `logging` | `logging/__init__.pyi` |
| `math` | `math/__init__.pyi` |
| `ntpath` | `ntpath.pyi` |
| `operator` | `operator.pyi` |
| `os` | `os/__init__.pyi` |
| `os.path` | `os/path.pyi` |
| `pathlib` | `pathlib/__init__.pyi` |
| `platform` | `platform.pyi` |
| `posixpath` | `posixpath.pyi` |
| `random` | `random.pyi` |
| `re` | `re.pyi` |
| `shlex` | `shlex.pyi` |
| `shutil` | `shutil.pyi` |
| `socket` | `socket.pyi` |
| `ssl` | `ssl.pyi` |
| `stat` | `stat.pyi` |
| `struct` | `struct.pyi` |
| `subprocess` | `subprocess.pyi` |
| `sys` | `sys/__init__.pyi` |
| `tempfile` | `tempfile.pyi` |
| `textwrap` | `textwrap.pyi` |
| `threading` | `threading.pyi` |
| `time` | `time.pyi` |
| `types` | `types.pyi` |
| `typing` | `typing.pyi` |
| `unittest` | `unittest/__init__.pyi` |
| `unittest.async_case` | `unittest/async_case.pyi` |
| `unittest.case` | `unittest/case.pyi` |
| `warnings` | `warnings.pyi` |
| `weakref` | `weakref.pyi` |
| `xml` | `xml/__init__.pyi` |
| `xml.dom` | `xml/dom/__init__.pyi` |
| `xml.dom.minidom` | `xml/dom/minidom.pyi` |
| `xml.etree.ElementTree` | `xml/etree/ElementTree.pyi` |
| `xml.etree` | `xml/etree/__init__.pyi` |
| `xml.sax` | `xml/sax/__init__.pyi` |

The next table is the AST-derived transitive import closure of those roots
for this exact typeshed revision. The producer currently parses imports but
does not discover omitted source entries, so these 149 paths are explicit
pack data until closure discovery moves into the engine producer. The closure
contains only `stdlib/` stubs; every parsed import target resolved there.

### Transitive import-closure stubs

| Added module | Pinned stub file |
| --- | --- |
| `_ast` | `_ast.pyi` |
| `_asyncio` | `_asyncio.pyi` |
| `_blake2` | `_blake2.pyi` |
| `_bz2` | `_bz2.pyi` |
| `_codecs` | `_codecs.pyi` |
| `_compression` | `_compression.pyi` |
| `_contextvars` | `_contextvars.pyi` |
| `_ctypes` | `_ctypes.pyi` |
| `_decimal` | `_decimal.pyi` |
| `_frozen_importlib` | `_frozen_importlib.pyi` |
| `_frozen_importlib_external` | `_frozen_importlib_external.pyi` |
| `_hashlib` | `_hashlib.pyi` |
| `_interpqueues` | `_interpqueues.pyi` |
| `_interpreters` | `_interpreters.pyi` |
| `_io` | `_io.pyi` |
| `_json` | `_json.pyi` |
| `_operator` | `_operator.pyi` |
| `_pickle` | `_pickle.pyi` |
| `_queue` | `_queue.pyi` |
| `_random` | `_random.pyi` |
| `_socket` | `_socket.pyi` |
| `_ssl` | `_ssl.pyi` |
| `_stat` | `_stat.pyi` |
| `_struct` | `_struct.pyi` |
| `_thread` | `_thread.pyi` |
| `_typeshed` | `_typeshed/__init__.pyi` |
| `_typeshed.importlib` | `_typeshed/importlib.pyi` |
| `_typeshed.xml` | `_typeshed/xml.pyi` |
| `_warnings` | `_warnings.pyi` |
| `_weakref` | `_weakref.pyi` |
| `_weakrefset` | `_weakrefset.pyi` |
| `_winapi` | `_winapi.pyi` |
| `_zstd` | `_zstd.pyi` |
| `annotationlib` | `annotationlib.pyi` |
| `ast` | `ast.pyi` |
| `asyncio` | `asyncio/__init__.pyi` |
| `asyncio.base_events` | `asyncio/base_events.pyi` |
| `asyncio.base_futures` | `asyncio/base_futures.pyi` |
| `asyncio.constants` | `asyncio/constants.pyi` |
| `asyncio.coroutines` | `asyncio/coroutines.pyi` |
| `asyncio.events` | `asyncio/events.pyi` |
| `asyncio.exceptions` | `asyncio/exceptions.pyi` |
| `asyncio.futures` | `asyncio/futures.pyi` |
| `asyncio.graph` | `asyncio/graph.pyi` |
| `asyncio.locks` | `asyncio/locks.pyi` |
| `asyncio.mixins` | `asyncio/mixins.pyi` |
| `asyncio.proactor_events` | `asyncio/proactor_events.pyi` |
| `asyncio.protocols` | `asyncio/protocols.pyi` |
| `asyncio.queues` | `asyncio/queues.pyi` |
| `asyncio.runners` | `asyncio/runners.pyi` |
| `asyncio.selector_events` | `asyncio/selector_events.pyi` |
| `asyncio.streams` | `asyncio/streams.pyi` |
| `asyncio.subprocess` | `asyncio/subprocess.pyi` |
| `asyncio.taskgroups` | `asyncio/taskgroups.pyi` |
| `asyncio.tasks` | `asyncio/tasks.pyi` |
| `asyncio.threads` | `asyncio/threads.pyi` |
| `asyncio.timeouts` | `asyncio/timeouts.pyi` |
| `asyncio.transports` | `asyncio/transports.pyi` |
| `asyncio.unix_events` | `asyncio/unix_events.pyi` |
| `asyncio.windows_events` | `asyncio/windows_events.pyi` |
| `asyncio.windows_utils` | `asyncio/windows_utils.pyi` |
| `bz2` | `bz2.pyi` |
| `compression` | `compression/__init__.pyi` |
| `compression._common` | `compression/_common/__init__.pyi` |
| `compression._common._streams` | `compression/_common/_streams.pyi` |
| `compression.zstd` | `compression/zstd/__init__.pyi` |
| `compression.zstd._zstdfile` | `compression/zstd/_zstdfile.pyi` |
| `concurrent` | `concurrent/__init__.pyi` |
| `concurrent.futures` | `concurrent/futures/__init__.pyi` |
| `concurrent.futures._base` | `concurrent/futures/_base.pyi` |
| `concurrent.futures.interpreter` | `concurrent/futures/interpreter.pyi` |
| `concurrent.futures.process` | `concurrent/futures/process.pyi` |
| `concurrent.futures.thread` | `concurrent/futures/thread.pyi` |
| `concurrent.interpreters` | `concurrent/interpreters/__init__.pyi` |
| `concurrent.interpreters._crossinterp` | `concurrent/interpreters/_crossinterp.pyi` |
| `concurrent.interpreters._queues` | `concurrent/interpreters/_queues.pyi` |
| `contextvars` | `contextvars.pyi` |
| `copyreg` | `copyreg.pyi` |
| `ctypes._endian` | `ctypes/_endian.pyi` |
| `decimal` | `decimal.pyi` |
| `dis` | `dis.pyi` |
| `fractions` | `fractions.pyi` |
| `genericpath` | `genericpath.pyi` |
| `gzip` | `gzip.pyi` |
| `importlib._abc` | `importlib/_abc.pyi` |
| `importlib._bootstrap` | `importlib/_bootstrap.pyi` |
| `importlib._bootstrap_external` | `importlib/_bootstrap_external.pyi` |
| `importlib.abc` | `importlib/abc.pyi` |
| `importlib.machinery` | `importlib/machinery.pyi` |
| `importlib.metadata._meta` | `importlib/metadata/_meta.pyi` |
| `importlib.readers` | `importlib/readers.pyi` |
| `importlib.resources` | `importlib/resources/__init__.pyi` |
| `importlib.resources._common` | `importlib/resources/_common.pyi` |
| `importlib.resources._functional` | `importlib/resources/_functional.pyi` |
| `importlib.resources.abc` | `importlib/resources/abc.pyi` |
| `multiprocessing` | `multiprocessing/__init__.pyi` |
| `multiprocessing.connection` | `multiprocessing/connection.pyi` |
| `multiprocessing.context` | `multiprocessing/context.pyi` |
| `multiprocessing.managers` | `multiprocessing/managers.pyi` |
| `multiprocessing.pool` | `multiprocessing/pool.pyi` |
| `multiprocessing.popen_fork` | `multiprocessing/popen_fork.pyi` |
| `multiprocessing.popen_forkserver` | `multiprocessing/popen_forkserver.pyi` |
| `multiprocessing.popen_spawn_posix` | `multiprocessing/popen_spawn_posix.pyi` |
| `multiprocessing.popen_spawn_win32` | `multiprocessing/popen_spawn_win32.pyi` |
| `multiprocessing.process` | `multiprocessing/process.pyi` |
| `multiprocessing.queues` | `multiprocessing/queues.pyi` |
| `multiprocessing.reduction` | `multiprocessing/reduction.pyi` |
| `multiprocessing.resource_sharer` | `multiprocessing/resource_sharer.pyi` |
| `multiprocessing.shared_memory` | `multiprocessing/shared_memory.pyi` |
| `multiprocessing.sharedctypes` | `multiprocessing/sharedctypes.pyi` |
| `multiprocessing.spawn` | `multiprocessing/spawn.pyi` |
| `multiprocessing.synchronize` | `multiprocessing/synchronize.pyi` |
| `multiprocessing.util` | `multiprocessing/util.pyi` |
| `numbers` | `numbers.pyi` |
| `opcode` | `opcode.pyi` |
| `pathlib.types` | `pathlib/types.pyi` |
| `pickle` | `pickle.pyi` |
| `pyexpat` | `pyexpat/__init__.pyi` |
| `pyexpat.errors` | `pyexpat/errors.pyi` |
| `pyexpat.model` | `pyexpat/model.pyi` |
| `queue` | `queue.pyi` |
| `resource` | `resource.pyi` |
| `selectors` | `selectors.pyi` |
| `signal` | `signal.pyi` |
| `string` | `string/__init__.pyi` |
| `sys.__jit` | `sys/__jit.pyi` |
| `sys._monitoring` | `sys/_monitoring.pyi` |
| `tarfile` | `tarfile.pyi` |
| `typing_extensions` | `typing_extensions.pyi` |
| `unittest._log` | `unittest/_log.pyi` |
| `unittest.loader` | `unittest/loader.pyi` |
| `unittest.main` | `unittest/main.pyi` |
| `unittest.result` | `unittest/result.pyi` |
| `unittest.runner` | `unittest/runner.pyi` |
| `unittest.signals` | `unittest/signals.pyi` |
| `unittest.suite` | `unittest/suite.pyi` |
| `xml.dom.domreg` | `xml/dom/domreg.pyi` |
| `xml.dom.minicompat` | `xml/dom/minicompat.pyi` |
| `xml.dom.xmlbuilder` | `xml/dom/xmlbuilder.pyi` |
| `xml.parsers` | `xml/parsers/__init__.pyi` |
| `xml.parsers.expat` | `xml/parsers/expat/__init__.pyi` |
| `xml.sax._exceptions` | `xml/sax/_exceptions.pyi` |
| `xml.sax.handler` | `xml/sax/handler.pyi` |
| `xml.sax.xmlreader` | `xml/sax/xmlreader.pyi` |
| `xml.utils` | `xml/utils.pyi` |
| `zipfile` | `zipfile/__init__.pyi` |
| `zipfile._path` | `zipfile/_path/__init__.pyi` |
| `zipimport` | `zipimport.pyi` |
| `zlib` | `zlib.pyi` |

The pack is one slice of the standard library, not the standard library. A
module outside this selected source set is outside the pack's statements and
cannot yield a standard-library absence verdict. The manifest stores one
`completeness` value for the whole `python_stub` source set, not a separate
value for each module; the Python boundary applies that pack value to each
module it publishes. This generated set is `complete`, with zero rejected or
suppressed stubs, so all 212 included module surfaces inherit complete
extraction status. Module-specific dynamic behavior, such as `__getattr__` or
an unenumerated `*` binding, still makes that module's boundary incomplete and
cannot prove a name absent.

`os.path`, `collections.abc`, `codecs`, and `struct` are re-export shims in
typeshed. Their stubs spell `from ntpath import *`, `from posixpath import *`,
`from _collections_abc import *`, `from _codecs import *`, and
`from _struct import *`.

The producer expands a wildcard whose module the same production carries. It
binds the names that module's literal `__all__` lists, or every public name it
binds when the module states no `__all__`, and it follows a chain of shims to
the class that declares each name. `os.path` and `collections.abc` are
expanded this way: `os.path.join` exists, and `collections.abc.MutableSet` is
published as an alias of `typing.MutableSet`, so `builtins.set` resolves its
base and a name that is not on `set` can be proved absent. A name a guarded
wildcard binds keeps that condition, so the `os.path` names carry the
`sys.platform` guard their branch states.

`_codecs` and `_struct` are in the pinned import closure. The generated pack
expands both wildcard re-exports: `codecs` publishes 99 names and `struct`
publishes 13, with no incomplete `*` marker. No newly added closure module has
an unenumerated `*` or dynamic `__getattr__` marker. A module whose `__all__`
this producer cannot read as a list of string literals keeps the marker for the
same reason.

Typeshed publishes overloaded methods as several records with one owner and
name. The semantic-model overlay treats such records as one present member
only when the active pack proves the complete callable family. Competing
fields, partial families, ambiguous records, and records from different packs
remain incomplete.

`builtins.pyi` declares `exit` and `quit` as values of the class
`_sitebuiltins.Quitter`, not as functions, and calling such a value invokes
its class's `__call__`. The producer projects that signature onto the value's
name: the generated pack publishes `builtins.exit` with the
`Quitter.__call__` contract, whose return annotation is `typing.Never`. A
guard whose arm calls `sys.exit`, `exit`, or `quit` therefore ends the arm,
and the class the guard excluded no longer reaches the code after the `if`
(#3135). The same projection publishes `copyright`, `credits`, `help`, and
`license` from their `_sitebuiltins` classes. A value annotation that names
no class this production declares, and a class without a declared
`__call__`, keeps the plain value binding without a callable record.

The producer omits `Protocol` and `Generic` class bases only when structured
import bindings resolve them to `typing` or `typing_extensions`. These are
typing-only class-construction markers rather than runtime inheritance
surfaces. A local or application-defined class with either name, and an
unresolved spelling, remains an ordinary base.

Typeshed supports Python 3.10 through 3.14, so the pack's compatibility and
activation name the `cpython` toolchain over that range. Typeshed guards
version-specific and platform-specific declarations with `sys.version_info`
and `sys.platform` blocks.

The producer keeps a pack static and still never evaluates a guard. It records
the guard on the declaration instead: an inclusive minimum toolchain version,
an exclusive maximum, and the activation targets the block requires or
excludes. Activation pins one exact interpreter version and one target, and it
drops a declaration only when a recorded constraint *provably* excludes that
interpreter. Under a cpython 3.13.5 Linux activation the pack therefore stops
resolving `builtins.float.from_number` (`sys.version_info >= (3, 14)`) and
`os.startfile` (`sys.platform == "win32"`), while every unguarded name resolves
as before.

The honesty rule runs one way only. A guard this producer cannot express, and
a coordinate the activation does not pin, both keep the declaration and mark it
as read incompletely rather than dropping it. Two branches that declare one
identity leave no branch's condition necessary, so that declaration stays
active for every activation as well.

Read a published name as "this interpreter declares this name, or its guard
could not be read". A name this slice covers and this activation dropped is one
the pinned interpreter provably does not declare. A name the slice never
covered is still outside the pack's statements, as the module table above
says.

## Reviewed assertion behavior

`unittest-assertions-2026.9.7.json` is a separate authored procedure-summary
pack. It records the reviewed CPython 3.10.0 through 3.14.0 normal-return contract for
`unittest.case.TestCase.assertIsInstance` at the two exact call arities (with
and without its optional `msg`). It deliberately does not claim coverage of
workspace overrides, and is activated alongside the declaration pack across
the same CPython `>=3.10.0, <3.15.0` range by the public build script. Release
measurement uses the exact CPython 3.13.5 selector.

The same pack records the reviewed identity-preserving `dataclasses.dataclass`
decorator. The direct decorator and factory form accept only structured literal
boolean keywords named by the pack. `slots` and `weakref_slot` are accepted only
when explicitly false; a dynamic value, positional or unpacked argument,
unknown keyword, or true slot option does not establish class identity. The
summary targets the canonical `dataclasses.dataclass` declaration with one
implicit class parameter and a variadic keyword tail. This is an identity
contract only: it does not claim that generated dataclass members are modeled.

An activation supplies its target as the interpreter's own `sys.platform`
value, which is the vocabulary typeshed's platform guards name. A target from
another vocabulary would read as an ordinary mismatch and could drop a
declaration the interpreter has.

## License

Typeshed is licensed under the Apache License, Version 2.0. The pinned
revision and the license are recorded in the specification's provenance and
in `notices/typeshed-stdlib-2026.8.31.txt`, which ships with the pack.

## Regeneration

`scripts/public/build-pinned-python-semantic-packs.sh OUTPUT_DIR WORK_DIR [CACHE_ROOT]` downloads
the pinned archive, checks its SHA-256, extracts the stub root under the
pinned directory name, and then generates and verifies the bundle. The
pinned artifact is a source set rather than one file, so its digest is the
canonical digest over the listed stub paths and bytes. Generation verifies
that digest itself and refuses a tree that differs.

When `CACHE_ROOT` is present, the recipe also installs the verified bundle
into the catalog version derived from Bifrost's current catalog schema and
writes `type-flow-python-pack-activation.json` at the cache root. The receipt
records the legacy declaration pack id/version and manifest digest together
with the catalog directory and absolute bundle path used by the corpus
measurement route. Its additive `packs` array records the complete activated
declaration and authored-pack identities; schema-1 single-pack receipts remain
readable. Omitting `CACHE_ROOT` preserves the generate-and-verify-only
workflow.

GitHub builds a source archive on demand. The archive digest that the script
checks is therefore a weaker pin than the artifact digest that `generate`
enforces: a change in GitHub's archive encoding would fail the script's
checksum without any change to the pack the specification names. Repin the
archive digest in that case; the pack digest and the pinned revision stay the
same.

To run the same steps by hand:

```console
cargo run --locked --release --features release-tooling -p brokk-bifrost-semantic-packs --bin bifrost-semantic-pack -- generate \
  /path/to/output \
  semantic-packs/python/typeshed-stdlib-2026.8.31.json /path/to/typeshed-stdlib-1620e2254765 \
  semantic-packs/python/unittest-assertions-2026.9.7.spec.json \
  semantic-packs/python/unittest-assertions-2026.9.7.json

cargo run --locked --release --features release-tooling -p brokk-bifrost-semantic-packs --bin bifrost-semantic-pack -- verify \
  /path/to/output
```
