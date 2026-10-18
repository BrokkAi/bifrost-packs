#!/usr/bin/env python3
"""Observe CPython 3.13.5 builtin and selected TestCase class bases.

This script intentionally imports only the Python standard library. It inspects
the executing interpreter's builtin type exports and exactly two pinned
TestCase exports, closed over actual ordered ``__bases__``. It never selects
workspace or typing classes. Selected stdlib source pins are not a hermetic
attestation of every transitive standard-library import.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import sysconfig
import tempfile


EXPECTED_VERSION = (3, 13, 5)
EXPECTED_EXECUTABLE_SHA256 = (
    "889c603f0d17cb54060951bcf4c4f9b8c9ebd9e52b392c70209bbb9755d797d9"
)
PACK_ID = "bifrost.python-runtime-bases"
PACK_VERSION = "1.1.0"
PRODUCER_NAME = "bifrost-cpython-runtime-base-observer"
PRODUCER_VERSION = "1.1.0"
SHARD_ID = "declarations.python-runtime-bases"
SELECTED_STDLIB_SOURCES = {
    "unittest": (
        "unittest/__init__.py",
        "7c22ee0c503b75aba5221e3e8189f9bf4632f85a43315ff841ec9d26a68e3551",
    ),
    "unittest.case": (
        "unittest/case.py",
        "ce2499ee6f34a9e6e24f11ae1e2f02e71a3529cca03d5488f0bdcfea8d5d8481",
    ),
}
SELECTION = (
    "all type exports in vars(builtins), plus exactly unittest.TestCase and "
    "unittest.case.TestCase, transitively closed over actual ordered __bases__"
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


def inspect_selected_modules() -> tuple[list[object], dict[str, object]]:
    """Pin both selected sources before importing either selected module."""
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ObservationError("selected stdlib observation requires -I -B")
    stdlib_root = Path(sysconfig.get_path("stdlib")).resolve(strict=True)
    paths = {}
    for name, (relative, expected_sha256) in SELECTED_STDLIB_SOURCES.items():
        if name in sys.modules:
            raise ObservationError(f"selected module was imported before source verification: {name}")
        path = (stdlib_root / relative).resolve(strict=True)
        if not path.is_relative_to(stdlib_root) or not path.is_file():
            raise ObservationError(f"selected source is outside the actual stdlib: {relative}")
        if sha256_file(path) != expected_sha256:
            raise ObservationError(f"selected stdlib source SHA-256 mismatch: {relative}")
        paths[name] = path

    spec = importlib.util.find_spec("unittest")
    if (
        spec is None
        or spec.origin is None
        or Path(spec.origin).resolve(strict=True) != paths["unittest"]
    ):
        raise ObservationError("unittest import does not select the pinned stdlib package")
    modules = [importlib.import_module(name) for name in SELECTED_STDLIB_SOURCES]
    sources = []
    for name, module in zip(SELECTED_STDLIB_SOURCES, modules):
        relative, expected_sha256 = SELECTED_STDLIB_SOURCES[name]
        actual_spec = module.__spec__
        if (
            module.__name__ != name
            or actual_spec is None
            or actual_spec.name != name
            or actual_spec.origin is None
            or Path(actual_spec.origin).resolve(strict=True) != paths[name]
            or Path(module.__file__).resolve(strict=True) != paths[name]
            or sha256_file(paths[name]) != expected_sha256
        ):
            raise ObservationError(f"selected module origin/source identity mismatch: {name}")
        sources.append(
            {"module": name, "path": relative, "origin": str(paths[name]), "sha256": expected_sha256}
        )
    return modules, {"stdlib_root": str(stdlib_root), "sources": sources}


def collect_runtime_classes() -> tuple[list[dict[str, object]], dict[str, object]]:
    """Collect builtin exports, exactly the selected exports, and base closure."""
    import builtins

    roots = [
        (f"{builtins.__name__}.{name}", value)
        for name, value in vars(builtins).items()
        if isinstance(value, type)
    ]
    selected_modules, module_identity = inspect_selected_modules()
    selected_classes = []
    for module in selected_modules:
        value = vars(module).get("TestCase")
        if not isinstance(value, type):
            raise ObservationError(f"selected export is not a class: {module.__name__}.TestCase")
        roots.append((f"{module.__name__}.TestCase", value))
        selected_classes.append(value)
    if selected_classes[0] is not selected_classes[1]:
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
        f"{item['module']} source {item['path']} sha256 {item['sha256']}"
        for item in module_identity["sources"]
    )
    revision = (
        "CPython 3.13.5 executable sha256 "
        f"{executable_sha256}; observer sha256 {script_sha256}; "
        f"input selection: {SELECTION}; selected-module pins: {selected_source_pins}"
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
        "schema_version": 2,
        "observer": {"sha256": script_sha256},
        "interpreter": {
            "implementation": "CPython",
            "version": "3.13.5",
            "optimization": 0,
            "executable_sha256": executable_sha256,
        },
        "selection": SELECTION,
        "selected_modules": module_identity,
        "scope_note": "Selected source pins and actual module origins only; not a hermetic attestation of all stdlib imports.",
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
