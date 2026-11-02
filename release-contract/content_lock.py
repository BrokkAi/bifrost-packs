"""Read, join and regenerate sharded content locks.

A content lock records each content file's path, SHA-256 and review metadata.
Release archives carry the single-file form: a JSON object whose ``files`` list
holds every entry and whose ``aggregate_sha256`` covers the path-sorted
``sha256  path`` lines. An authoring checkout may instead keep only a header in
the lock file and spread the entries over shard files, so independent changes
touch different files and no stored line changes on every edit. The header's
``file_shards`` object names the shard directory and how deeply each path
prefix is sharded; the longest matching prefix wins:

    "file_shards": {"directory": "content-lock", "depths": {"": 2, "fixtures/": 3}}

A path is stored in ``<directory>/<first depth components>.json``; a file
directly inside a shallower directory uses that directory's shard. Joining the
shards yields the single-file form: the header without ``file_shards``, then the
path-sorted ``files``, then the computed ``aggregate_sha256``.

The module has no repository-specific paths. Callers supply the content
inventory, the entry for a new file and their own schema validation.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable


SHARD_KEY = "file_shards"


class LockError(Exception):
    """An invalid lock, shard or content path."""


def safe_relative_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise LockError(f"{field} must be a non-empty relative path")
    if "\x00" in value or "\\" in value or ":" in value:
        raise LockError(f"unsafe {field}: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith("/"):
        raise LockError(f"unsafe {field}: absolute paths are not allowed")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise LockError(f"unsafe {field}: path must be normalized: {value!r}")
    if path.as_posix() != value:
        raise LockError(f"unsafe {field}: path must use normalized POSIX form")
    return value


def regular_file(root: Path, relative: str) -> Path:
    """Return a regular file, rejecting symlinks in every path component."""
    safe_path = safe_relative_path(relative, "file path")
    current = Path(root)
    for part in safe_path.split("/"):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError as error:
            raise LockError(f"required file is missing: {safe_path}") from error
        except OSError as error:
            raise LockError(f"cannot inspect {safe_path}: {error}") from error
        if stat.S_ISLNK(mode):
            raise LockError(f"symlinks are not allowed in content paths: {safe_path}")
    if not stat.S_ISREG(mode):
        raise LockError(f"content path is not a regular file: {safe_path}")
    return current


def read_json(root: Path, relative: str) -> Any:
    """Read JSON from a regular file, rejecting duplicate object keys."""
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LockError(f"duplicate JSON key in {relative}: {key!r}")
            result[key] = value
        return result

    path = regular_file(root, relative)
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except json.JSONDecodeError as error:
        raise LockError(f"invalid JSON in {relative}: {error}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise LockError(f"cannot read {relative}: {error}") from error


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate_sha256(files: Iterable[dict[str, Any]]) -> str:
    """Return the digest of the path-sorted 'sha256  path' lines."""
    lines = [
        f"{entry['sha256']}  {entry['path']}\n"
        for entry in sorted(files, key=lambda entry: entry["path"])
    ]
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def lock_bytes(lock: dict[str, Any]) -> bytes:
    """Serialize a single-file lock exactly as archives carry it."""
    return (json.dumps(lock, indent=2) + "\n").encode("utf-8")


def _shard_bytes(entries: list[dict[str, Any]]) -> bytes:
    return (json.dumps({"files": entries}, indent=2) + "\n").encode("utf-8")


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LockError(f"{field} must be an object")
    return value


def read_header(root: Path, lock_name: str) -> dict[str, Any]:
    if (Path(root) / lock_name).is_symlink():
        raise LockError(f"{lock_name} must not be a symlink")
    return _require_mapping(read_json(root, lock_name), "lock")


def is_sharded(header: dict[str, Any]) -> bool:
    return SHARD_KEY in header


def shard_layout(header: dict[str, Any]) -> tuple[str, dict[str, int]]:
    """Return the validated shard directory and prefix depths of a header."""
    config = _require_mapping(header.get(SHARD_KEY), SHARD_KEY)
    if set(config) != {"directory", "depths"}:
        raise LockError(f"{SHARD_KEY} must contain exactly directory and depths")
    directory = safe_relative_path(config["directory"], f"{SHARD_KEY}.directory")
    depths = _require_mapping(config["depths"], f"{SHARD_KEY}.depths")
    if not depths:
        raise LockError(f"{SHARD_KEY}.depths must not be empty")
    for prefix, depth in depths.items():
        if prefix:
            if not prefix.endswith("/"):
                raise LockError(f"{SHARD_KEY}.depths prefix must be empty or end with '/': {prefix!r}")
            safe_relative_path(prefix[:-1], f"{SHARD_KEY}.depths prefix")
        if isinstance(depth, bool) or not isinstance(depth, int) or depth < 1:
            raise LockError(f"{SHARD_KEY}.depths[{prefix!r}] must be a positive integer")
    return directory, depths


def shard_name(depths: dict[str, int], path: str) -> str:
    """Return the shard for a path, relative to the shard directory without .json."""
    prefix = max((prefix for prefix in depths if path.startswith(prefix)), key=len, default=None)
    if prefix is None:
        raise LockError(f"no {SHARD_KEY} depth covers {path}")
    parts = path.split("/")
    name = "/".join(parts[: min(depths[prefix], len(parts) - 1)])
    if not name:
        raise LockError(f"a top-level file cannot be sharded: {path}")
    return name


def list_shards(root: Path, directory: str) -> list[str]:
    """Return shard names, rejecting anything but regular .json files."""
    base = Path(root) / directory
    try:
        mode = base.lstat().st_mode
    except FileNotFoundError:
        return []
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise LockError(f"{directory} must be a real directory")
    names = []
    for current_dir, directory_names, file_names in os.walk(base, followlinks=False):
        current = Path(current_dir)
        for name in directory_names:
            if (current / name).is_symlink():
                relative = (current / name).relative_to(root).as_posix()
                raise LockError(f"symlink directory is not allowed: {relative}")
        for name in file_names:
            relative = (current / name).relative_to(base).as_posix()
            if not relative.endswith(".json"):
                raise LockError(f"unexpected file in {directory}: {relative}")
            names.append(relative[: -len(".json")])
    return sorted(names)


def read_shard_entries(root: Path, header: dict[str, Any], *, strict: bool, fix_hint: str) -> list[dict[str, Any]]:
    """Read every shard. Strict reads also require canonical placement and form."""
    directory, depths = shard_layout(header)
    entries = []
    for name in list_shards(root, directory):
        relative = f"{directory}/{name}.json"
        shard = _require_mapping(read_json(root, relative), relative)
        if set(shard) != {"files"} or not isinstance(shard["files"], list):
            raise LockError(f"{relative} must contain only a files list")
        files = shard["files"]
        for index, item in enumerate(files):
            entry = _require_mapping(item, f"{relative} files[{index}]")
            path = safe_relative_path(entry.get("path"), f"{relative} files[{index}].path")
            if strict and shard_name(depths, path) != name:
                raise LockError(
                    f"{path} belongs in {directory}/{shard_name(depths, path)}.json, "
                    f"not {relative}; {fix_hint}"
                )
        if strict:
            if not files:
                raise LockError(f"{relative} is empty; {fix_hint}")
            canonical = sorted(files, key=lambda entry: entry["path"])
            if (Path(root) / relative).read_bytes() != _shard_bytes(canonical):
                raise LockError(f"{relative} is not in canonical form; {fix_hint}")
        entries.extend(files)
    return entries


def join(header: dict[str, Any], files: list[dict[str, Any]]) -> dict[str, Any]:
    """Join a header and entries into the single-file lock form."""
    lock = {key: value for key, value in header.items() if key not in (SHARD_KEY, "files", "aggregate_sha256")}
    lock["files"] = sorted(files, key=lambda entry: entry["path"])
    lock["aggregate_sha256"] = aggregate_sha256(lock["files"])
    return lock


def read_lock(root: Path, lock_name: str, *, fix_hint: str = "regenerate the lock") -> dict[str, Any]:
    """Return the single-file lock, joining strict shards when the header has them.

    A single-file lock is returned as stored; its aggregate and content bytes
    are the caller's to verify. A sharded header must not store files or an
    aggregate.
    """
    header = read_header(root, lock_name)
    if not is_sharded(header):
        return header
    for key in ("files", "aggregate_sha256"):
        if key in header:
            raise LockError(f"a sharded {lock_name} must not store {key}; it is derived from the shards")
    return join(header, read_shard_entries(root, header, strict=True, fix_hint=fix_hint))


def update_lock(
    root: Path,
    lock_name: str,
    *,
    content_paths: set[str],
    new_entry: Callable[[str, str], dict[str, Any] | None],
    default_layout: dict[str, Any],
    validate: Callable[[dict[str, Any]], Any] = lambda lock: lock,
) -> dict[str, list[str]]:
    """Rewrite the sharded lock from the content inventory.

    Entries for paths outside ``content_paths`` are dropped and changed digests
    are refreshed; every other recorded field is kept. ``new_entry(path,
    sha256)`` returns the entry for an unlisted file, or None to leave it
    unlisted. A single-file lock is converted using ``default_layout``. The
    joined lock is passed to ``validate`` before anything is written.
    """
    root = Path(root)
    header = read_header(root, lock_name)
    if is_sharded(header):
        entries = read_shard_entries(root, header, strict=False, fix_hint="")
    else:
        entries = header.get("files")
        if not isinstance(entries, list):
            raise LockError("files must be a list")
        header = dict(header, **{SHARD_KEY: default_layout})
    header = {key: value for key, value in header.items() if key not in ("files", "aggregate_sha256")}
    directory, depths = shard_layout(header)

    by_path: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(entries):
        entry = _require_mapping(item, f"files[{index}]")
        path = safe_relative_path(entry.get("path"), f"files[{index}].path")
        previous = by_path.get(path)
        if previous is not None:
            # Both sides of a merge may keep the same entry; only the digest may differ.
            if {k: v for k, v in previous.items() if k != "sha256"} != {k: v for k, v in entry.items() if k != "sha256"}:
                raise LockError(f"conflicting entries for {path}; keep one and rerun")
            continue
        by_path[path] = entry

    changes: dict[str, list[str]] = {"added": [], "updated": [], "removed": [], "unlisted": []}
    for path in sorted(set(by_path) - content_paths):
        del by_path[path]
        changes["removed"].append(path)
    for path, entry in sorted(by_path.items()):
        digest = sha256_file(regular_file(root, path))
        if entry.get("sha256") != digest:
            entry["sha256"] = digest
            changes["updated"].append(path)
    for path in sorted(content_paths - set(by_path)):
        entry = new_entry(path, sha256_file(regular_file(root, path)))
        if entry is None:
            changes["unlisted"].append(path)
        else:
            by_path[path] = entry
            changes["added"].append(path)

    shards: dict[str, list[dict[str, Any]]] = {}
    for path, entry in sorted(by_path.items()):
        shards.setdefault(shard_name(depths, path), []).append(entry)
    validate(join(header, list(by_path.values())))

    base = root / directory
    for name in set(list_shards(root, directory)) - set(shards):
        (base / f"{name}.json").unlink()
    for name, shard_entries in shards.items():
        target = base / f"{name}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        data = _shard_bytes(shard_entries)
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    for current, _, _ in sorted(os.walk(base), reverse=True):
        if current != str(base) and not os.listdir(current):
            os.rmdir(current)
    (root / lock_name).write_text(json.dumps(header, indent=2) + "\n", encoding="utf-8")
    return changes
