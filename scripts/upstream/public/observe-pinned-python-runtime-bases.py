#!/usr/bin/env python3
"""Observe CPython 3.13.5 builtin and selected standard-library class bases.

This script intentionally imports only the Python standard library. It inspects
the executing interpreter's builtin type exports and selected TestCase,
MutableMapping, Thread and WSGIRequestHandler exports, closed over actual ordered ``__bases__``.
It never selects workspace or typing classes. Frozen ABC modules are verified
as frozen objects; companion file pins do not attest executed frozen code.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile


EXPECTED_VERSION = (3, 13, 5)
EXPECTED_EXECUTABLE_SHA256 = (
    "889c603f0d17cb54060951bcf4c4f9b8c9ebd9e52b392c70209bbb9755d797d9"
)
PACK_ID = "bifrost.python-runtime-bases"
PACK_VERSION = "1.3.0"
PRODUCER_NAME = "bifrost-cpython-runtime-base-observer"
PRODUCER_VERSION = "1.3.0"
SHARD_ID = "declarations.python-runtime-bases"
SELECTED_STDLIB_SOURCES = {
    "threading": (
        "threading.py",
        "61e1cd79adb93cfacf69dc3900ea99fbc8042d65f3742233c07c5707e39add84",
    ),
    "unittest": (
        "unittest/__init__.py",
        "7c22ee0c503b75aba5221e3e8189f9bf4632f85a43315ff841ec9d26a68e3551",
    ),
    "unittest.case": (
        "unittest/case.py",
        "ce2499ee6f34a9e6e24f11ae1e2f02e71a3529cca03d5488f0bdcfea8d5d8481",
    ),
    "wsgiref": (
        "wsgiref/__init__.py",
        "c30e144025a63d267778d92f2f066fa592b476e789d888f79b96c059bf0bef60",
    ),
    "socketserver": (
        "socketserver.py",
        "ecbbe1a633801460399a8f10b39007aa0e13cdbdad507e39414000f097b769b5",
    ),
    "http": (
        "http/__init__.py",
        "d5747ca51f40e43b2366ce430154af22ce02d8d5972a6e81afb54ca946f684c0",
    ),
    "http.server": (
        "http/server.py",
        "253cc04a379f2a42dc72c33a9a67218ecda13b54995b72c3f59e83d1abe8e9a3",
    ),
    "wsgiref.simple_server": (
        "wsgiref/simple_server.py",
        "d6b820a6addc837717989064565d5be0c18af67337700ad48b317825eb4a13d8",
    ),
}
FROZEN_COMPANION_SOURCES = {
    "_collections_abc": (
        "_collections_abc.py",
        "2cfe340c4cf54077f054cd366a2c7a515e9ee8da7d8b3fa071251f280034756d",
    ),
    "collections": (
        "collections/__init__.py",
        "2347f647577b6c11b82fc48fa4a1744f7af1af87f15942f92b7cc4410f0a817b",
    ),
}
SELECTED_EXPORTS = (
    ("unittest", "TestCase"),
    ("unittest.case", "TestCase"),
    ("collections.abc", "MutableMapping"),
    ("_collections_abc", "MutableMapping"),
    ("threading", "Thread"),
    ("wsgiref.simple_server", "WSGIRequestHandler"),
)
SELECTION = (
    "all type exports in vars(builtins), plus exactly "
    + ", ".join(f"{module}.{name}" for module, name in SELECTED_EXPORTS)
    + ", transitively closed over actual ordered __bases__"
)


class ObservationError(ValueError):
    """The active interpreter or observed class graph is outside the contract."""


def has_control_character(value: str) -> bool:
    return any(ord(character) < 32 or 0x7F <= ord(character) <= 0x9F for character in value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def qualified_name(cls: type) -> str:
    """Read names through ``type`` to bypass custom metaclass overrides."""
    module = type.__getattribute__(cls, "__module__")
    qualname = type.__getattribute__(cls, "__qualname__")
    if not isinstance(module, str) or not module or not isinstance(qualname, str) or not qualname:
        raise ObservationError("observed class has no stable string __module__/__qualname__")
    if any(character.isspace() for character in module + qualname) or has_control_character(
        module + qualname
    ):
        raise ObservationError("observed class name contains whitespace or control characters")
    return f"{module}.{qualname}"


def inspect_interpreter() -> tuple[str, str]:
    if sys.implementation.name != "cpython":
        raise ObservationError(f"expected CPython, found {sys.implementation.name!r}")
    if sys.version_info[:3] != EXPECTED_VERSION:
        raise ObservationError(
            f"expected CPython 3.13.5, found {sys.version_info.major}."
            f"{sys.version_info.minor}.{sys.version_info.micro}"
        )
    if sys.flags.optimize != 0 or not __debug__:
        raise ObservationError("interpreter must run without optimization (-O/-OO)")

    executable = Path(sys.executable).resolve(strict=True)
    executable_sha256 = sha256_file(executable)
    if executable_sha256 != EXPECTED_EXECUTABLE_SHA256:
        raise ObservationError(
            "interpreter executable SHA-256 mismatch: "
            f"expected {EXPECTED_EXECUTABLE_SHA256}, found {executable_sha256}"
        )

    script = Path(__file__).resolve(strict=True)
    return executable_sha256, sha256_file(script)


def verify_stdlib_sources(
    stdlib_root: Path, sources: dict[str, tuple[str, str]]
) -> dict[str, Path]:
    paths = {}
    for name, (relative, expected_sha256) in sources.items():
        path = (stdlib_root / relative).resolve(strict=True)
        if not path.is_relative_to(stdlib_root) or not path.is_file():
            raise ObservationError(f"selected file is outside the actual stdlib: {relative}")
        if sha256_file(path) != expected_sha256:
            raise ObservationError(f"selected stdlib file SHA-256 mismatch: {relative}")
        paths[name] = path
    return paths


def inspect_selected_modules() -> tuple[dict[str, object], dict[str, object]]:
    """Pin fresh selected and canonical-owner sources before importing modules."""
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ObservationError("selected stdlib observation requires -I -B")
    # Importing sysconfig itself loads threading on the pinned interpreter.
    # Bootstrap from CPython's runtime directory, pin fresh sources first, then
    # require the ordinary sysconfig root to agree before selecting any class.
    stdlib_root = Path(sys._stdlib_dir).resolve(strict=True)
    for name in SELECTED_STDLIB_SOURCES:
        if name in sys.modules:
            raise ObservationError(f"selected module was imported before source verification: {name}")
    paths = verify_stdlib_sources(stdlib_root, SELECTED_STDLIB_SOURCES)
    import sysconfig

    if Path(sysconfig.get_path("stdlib")).resolve(strict=True) != stdlib_root:
        raise ObservationError("CPython runtime stdlib directory and sysconfig root disagree")
    for name in ("threading", "unittest", "wsgiref", "socketserver", "http"):
        spec = importlib.util.find_spec(name)
        if spec is None or spec.origin is None or Path(spec.origin).resolve(strict=True) != paths[name]:
            raise ObservationError(f"import does not select the pinned stdlib module: {name}")
    modules = {name: importlib.import_module(name) for name in SELECTED_STDLIB_SOURCES}
    sources = []
    for name, module in modules.items():
        relative, expected_sha256 = SELECTED_STDLIB_SOURCES[name]
        actual_spec = module.__spec__
        if (
            module.__name__ != name
            or actual_spec is None
            or actual_spec.name != name
            or actual_spec.origin is None
            or Path(actual_spec.origin).resolve(strict=True) != paths[name]
            or Path(module.__file__).resolve(strict=True) != paths[name]
            or sys.modules.get(name) is not module
            or sha256_file(paths[name]) != expected_sha256
        ):
            raise ObservationError(f"selected module origin/source identity mismatch: {name}")
        sources.append(
            {"module": name, "path": relative, "origin": str(paths[name]),
             "sha256": expected_sha256, "role": "fresh_module_source",
             "preloaded": False, "module_name": module.__name__, "spec_name": actual_spec.name}
        )
    return modules, {"stdlib_root": str(stdlib_root), "sources": sources}


def inspect_frozen_abc_modules() -> tuple[dict[str, object], dict[str, object]]:
    """Accept honest preload; verify frozen identities, not companion-code equivalence."""
    import sysconfig

    stdlib_root = Path(sysconfig.get_path("stdlib")).resolve(strict=True)
    names = ("collections", "collections.abc", "_collections_abc")
    preloaded = {name: name in sys.modules for name in names}
    paths = verify_stdlib_sources(stdlib_root, FROZEN_COMPANION_SOURCES)
    modules = {name: importlib.import_module(name) for name in names}
    private = modules["_collections_abc"]
    if (
        modules["collections.abc"] is not private
        or vars(modules["collections"]).get("abc") is not private
        or vars(modules["collections.abc"]).get("MutableMapping")
        is not vars(private).get("MutableMapping")
    ):
        raise ObservationError("public/private ABC module or MutableMapping identity mismatch")
    frozen_spec = importlib.machinery.FrozenImporter.find_spec("_collections_abc")
    if (
        frozen_spec is None or frozen_spec.origin != "frozen"
        or frozen_spec.loader is not importlib.machinery.FrozenImporter
    ):
        raise ObservationError("the ABC import is not provided by FrozenImporter")
    identities = []
    for name, module in modules.items():
        spec = module.__spec__
        if sys.modules.get(name) is not module or spec is None:
            raise ObservationError(f"module binding/spec mismatch: {name}")
        if name == "collections":
            if (
                module.__name__ != name or spec.name != name
                or spec.origin is None
                or Path(spec.origin).resolve(strict=True) != paths[name]
                or Path(module.__file__).resolve(strict=True) != paths[name]
            ):
                raise ObservationError("collections origin does not match the retained companion file")
        elif (
            module.__name__ != "collections.abc" or spec.name != "_collections_abc"
            or spec.origin != "frozen"
            or spec.loader is not importlib.machinery.FrozenImporter
            or module.__loader__ is not importlib.machinery.FrozenImporter
            or sys.modules.get(spec.name) is not module
            or Path(module.__file__).resolve(strict=True) != paths["_collections_abc"]
        ):
            raise ObservationError(f"frozen ABC identity/spec/origin mismatch: {name}")
        identities.append(
            {"binding": name, "module_name": module.__name__, "spec_name": spec.name,
             "origin": spec.origin, "file": str(Path(module.__file__).resolve(strict=True)),
             "loader": (f"{spec.loader.__module__}.{spec.loader.__qualname__}"
                        if name != "collections" else
                        f"{type(spec.loader).__module__}.{type(spec.loader).__qualname__}"),
             "preloaded": preloaded[name]}
        )
    verify_stdlib_sources(stdlib_root, FROZEN_COMPANION_SOURCES)
    companions = [
        {"module": name, "path": relative, "origin": str(paths[name]),
         "sha256": digest, "role": "retained_companion_file"}
        for name, (relative, digest) in FROZEN_COMPANION_SOURCES.items()
    ]
    return modules, {"sources": companions, "module_bindings": identities,
                     "public_private_module_same": True, "public_private_class_same": True,
                     "scope_note": "Companion file pins are not executed frozen-code equivalence."}


def collect_runtime_classes() -> tuple[list[dict[str, object]], dict[str, object]]:
    """Collect builtin exports, exactly the selected exports, and base closure."""
    import builtins

    roots = [
        (f"{builtins.__name__}.{name}", value)
        for name, value in vars(builtins).items()
        if isinstance(value, type)
    ]
    selected_modules, module_identity = inspect_selected_modules()
    frozen_modules, frozen_identity = inspect_frozen_abc_modules()
    selected_modules.update(frozen_modules)
    module_identity["sources"].extend(frozen_identity.pop("sources"))
    module_identity["frozen_abc"] = frozen_identity
    for module_name, export_name in SELECTED_EXPORTS:
        value = vars(selected_modules[module_name]).get(export_name)
        if not isinstance(value, type):
            raise ObservationError(f"selected export is not a class: {module_name}.{export_name}")
        # Bind aliases to the requested import binding, not module.__name__:
        # both ABC import names intentionally share one frozen module object.
        roots.append((f"{module_name}.{export_name}", value))
    if vars(selected_modules["unittest"])["TestCase"] is not vars(selected_modules["unittest.case"])["TestCase"]:
        raise ObservationError("selected TestCase exports do not name the same class object")

    classes_by_identity: dict[int, type] = {}
    exported_names_by_identity: dict[int, list[str]] = {}
    pending: list[type] = []
    for name, cls in roots:
        identity = id(cls)
        classes_by_identity[identity] = cls
        exported_names_by_identity.setdefault(identity, []).append(name)
        pending.append(cls)

    while pending:
        cls = pending.pop()
        for base in type.__getattribute__(cls, "__bases__"):
            identity = id(base)
            previous = classes_by_identity.get(identity)
            if previous is None:
                classes_by_identity[identity] = base
                exported_names_by_identity[identity] = []
                pending.append(base)
            elif previous is not base:
                raise ObservationError("runtime object identity collision during base traversal")

    canonical_by_name: dict[str, type] = {}
    records: list[dict[str, object]] = []
    names_by_identity: dict[int, str] = {}
    for identity, cls in classes_by_identity.items():
        name = qualified_name(cls)
        previous = canonical_by_name.get(name)
        if previous is not None and previous is not cls:
            raise ObservationError(
                f"distinct runtime classes share canonical name {name!r}"
            )
        canonical_by_name[name] = cls
        names_by_identity[identity] = name

    for identity, cls in classes_by_identity.items():
        bases = type.__getattribute__(cls, "__bases__")
        mro = type.__getattribute__(cls, "__mro__")
        try:
            base_names = [names_by_identity[id(base)] for base in bases]
            mro_names = [names_by_identity[id(item)] for item in mro]
        except KeyError as error:
            raise ObservationError("runtime base/MRO class escaped the observed closure") from error
        records.append(
            {
                "canonical_name": names_by_identity[identity],
                "exports": sorted(exported_names_by_identity[identity]),
                "bases": base_names,
                "mro": mro_names,
            }
        )

    records.sort(key=lambda record: record["canonical_name"])
    return records, module_identity


def stable_type_id(canonical_name: str) -> str:
    # Stable model IDs are lowercase ASCII; Python names retain their case.
    if not canonical_name.isascii():
        raise ObservationError(f"non-ASCII runtime class name: {canonical_name!r}")
    identifier = f"type.python.{canonical_name.lower()}"
    if len(identifier) > 256 or re.fullmatch(
        r"[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?", identifier
    ) is None:
        raise ObservationError(f"runtime class has no valid stable ID: {canonical_name!r}")
    return identifier


def build_outputs(
    records: list[dict[str, object]],
    executable_sha256: str,
    script_sha256: str,
    module_identity: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    id_by_name: dict[str, str] = {}
    name_by_id: dict[str, str] = {}
    for record in records:
        name = record["canonical_name"]
        identifier = stable_type_id(name)
        if identifier in name_by_id:
            raise ObservationError(
                f"runtime class ID collision: {name_by_id[identifier]!r} and "
                f"{name!r} map to {identifier!r}"
            )
        id_by_name[name] = identifier
        name_by_id[identifier] = name
    source = f"CPython runtime observation: {SELECTION}; no workspace imports"
    selected_source_pins = "; ".join(
        f"{item['module']} {item['role']} {item['path']} sha256 {item['sha256']}"
        for item in module_identity["sources"]
    )
    revision = (
        "CPython 3.13.5 executable sha256 "
        f"{executable_sha256}; observer sha256 {script_sha256}; "
        f"input selection: {SELECTION}; selected-module file pins: {selected_source_pins}; "
        "ABC bindings verified against actual frozen origin/FrozenImporter; "
        "companion pins are not executed frozen-code equivalence"
    )
    activation = [
        {"toolchain": {"name": "cpython", "version": "=3.13.5"}, "targets": []}
    ]

    types = []
    for record in records:
        canonical_name = record["canonical_name"]
        aliases = [name for name in record["exports"] if name != canonical_name]
        types.append(
            {
                "id": id_by_name[canonical_name],
                "name": canonical_name,
                "type_kind": "class",
                "visibility": "public",
                "runtime_bases": [
                    {
                        "kind": "declared",
                        "id": id_by_name[base_name],
                        "arguments": [],
                        "nullable": False,
                    }
                    for base_name in record["bases"]
                ],
                "aliases": aliases,
                "locator": {
                    "kind": "artifact",
                    "path": "cpython-3.13.5-runtime",
                    "symbol": canonical_name,
                },
            }
        )

    model = {
        "schema_version": 17,
        "pack_id": PACK_ID,
        "version": PACK_VERSION,
        "producer": {"name": PRODUCER_NAME, "version": PRODUCER_VERSION},
        "language": "python",
        "ecosystem": "python",
        "compatibility": {
            "toolchains": [{"name": "cpython", "requirement": "=3.13.5"}]
        },
        "provenance": {"source": source, "revision": revision},
        "license": "PSF-2.0",
        "completeness": "partial",
        "safety": {"generated_code_only": False, "review_required": True},
        "shards": [
            {
                "id": SHARD_ID,
                "activation": activation,
                "payload": {"kind": "declaration_facts", "types": types},
            }
        ],
    }
    observations = {
        "schema_version": 3,
        "observer": {"sha256": script_sha256},
        "interpreter": {
            "implementation": "CPython",
            "version": "3.13.5",
            "optimization": 0,
            "executable_sha256": executable_sha256,
        },
        "selection": SELECTION,
        "selected_modules": module_identity,
        "scope_note": "Fresh selected sources, actual frozen module identities and companion file pins; not executed frozen-code equivalence or hermetic stdlib attestation.",
        "identity_note": "Class identity is observed by object identity in this process and recorded by actual __module__.__qualname__; no process address is serialized.",
        "exports": [
            {"name": alias, "canonical_name": record["canonical_name"]}
            for record in records
            for alias in record["exports"]
        ],
        "classes": records,
    }
    return model, observations


def encode_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write_pair(first: Path, first_data: bytes, second: Path, second_data: bytes) -> None:
    first = first.resolve()
    second = second.resolve()
    if first == second:
        raise ObservationError("model and raw observation outputs must be different paths")
    staged: list[tuple[Path, Path]] = []
    try:
        for destination, data in ((first, first_data), (second, second_data)):
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=f".{destination.name}.", suffix=".tmp",
                dir=destination.parent, delete=False
            ) as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                staged.append((Path(stream.name), destination))
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-output", required=True, type=Path)
    parser.add_argument("--observations-output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        executable_sha256, script_sha256 = inspect_interpreter()
        records, module_identity = collect_runtime_classes()
        if not records:
            raise ObservationError("builtins selection produced no class objects")
        model, observations = build_outputs(
            records, executable_sha256, script_sha256, module_identity
        )
        atomic_write_pair(
            args.model_output,
            encode_json(model),
            args.observations_output,
            encode_json(observations),
        )
    except (OSError, ObservationError) as error:
        print(f"runtime-base observation failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
