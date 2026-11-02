#!/usr/bin/env python3
"""Verify, lock and create reproducible source bundles for public pack content."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import stat
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "release-contract"))
import content_lock  # noqa: E402


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LOCK_NAME = "content-lock.json"
# Shard layout for converting a single-file lock (see release-contract/content_lock.py).
# Once converted, the lock header records the layout and is authoritative.
DEFAULT_FILE_SHARDS = {
    "directory": "content-lock",
    "depths": {
        "": 2,
        "fixtures/policy/": 4,
        "fixtures/semantic/": 3,
        "licenses/": 1,
        "semantic-packs/embedded/": 3,
    },
}
LOCK_FIX_HINT = "run scripts/content.py lock"
CONTENT_ROOTS = ("rules", "semantic-packs", "fixtures", "scripts/upstream", "licenses")
BUNDLE_METADATA = ("LICENSE", "NOTICE.md", "README.md", LOCK_NAME)
OPTIONAL_BUNDLE_METADATA = ("validation.json", "release-config.json", "scripts/content.py", "scripts/verify-native.py", "scripts/smoke.py")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")


# Lock errors and content path checks are shared with the release contract.
ContentError = content_lock.LockError
_safe_relative_path = content_lock.safe_relative_path
_regular_file = content_lock.regular_file
_sha256_file = content_lock.sha256_file
aggregate_sha256 = content_lock.aggregate_sha256
lock_bytes = content_lock.lock_bytes


def _is_content_path(path: str) -> bool:
    return any(path.startswith(root + "/") for root in CONTENT_ROOTS)


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentError(f"{field} must be an object")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContentError(f"{field} must be a non-empty string")
    return value


def _validate_lock(lock: Any) -> dict[str, Any]:
    lock = _require_mapping(lock, "lock")
    if lock.get("schema_version") != 1:
        raise ContentError("schema_version must be 1")
    content_version = _require_string(lock.get("content_version"), "content_version")
    if not VERSION_RE.fullmatch(content_version):
        raise ContentError("content_version must be a semantic version")

    source = _require_mapping(lock.get("source"), "source")
    _require_string(source.get("repository"), "source.repository")
    revision = _require_string(source.get("revision"), "source.revision")
    if not REVISION_RE.fullmatch(revision):
        raise ContentError("source.revision must be a full 40-character commit SHA")

    engine = _require_mapping(lock.get("engine"), "engine")
    first_default = _require_string(
        engine.get("first_default_version"), "engine.first_default_version"
    )
    if not VERSION_RE.fullmatch(first_default):
        raise ContentError("engine.first_default_version must be a semantic version")
    qualification_revision = _require_string(
        engine.get("qualification_revision"), "engine.qualification_revision"
    )
    if not REVISION_RE.fullmatch(qualification_revision):
        raise ContentError(
            "engine.qualification_revision must be a full 40-character commit SHA"
        )
    if engine.get("default_enabled") is not False:
        raise ContentError("engine.default_enabled must be false")
    qualified_versions = engine.get("qualified_versions")
    if not isinstance(qualified_versions, list):
        raise ContentError("engine.qualified_versions must be an explicit list")
    if any(
        not isinstance(version, str) or not VERSION_RE.fullmatch(version)
        for version in qualified_versions
    ):
        raise ContentError("engine.qualified_versions entries must be semantic versions")
    if len(set(qualified_versions)) != len(qualified_versions):
        raise ContentError("engine.qualified_versions must not contain duplicates")

    files = lock.get("files")
    if not isinstance(files, list):
        raise ContentError("files must be a list")
    seen_paths: set[str] = set()
    for index, item in enumerate(files):
        field = f"files[{index}]"
        entry = _require_mapping(item, field)
        path = _safe_relative_path(entry.get("path"), f"{field}.path")
        if not _is_content_path(path):
            raise ContentError(
                f"{field}.path must be under one of: {', '.join(CONTENT_ROOTS)}"
            )
        _safe_relative_path(entry.get("source_path"), f"{field}.source_path")
        if "source_revision" in entry:
            source_revision = entry["source_revision"]
            if not isinstance(source_revision, str) or not REVISION_RE.fullmatch(source_revision):
                raise ContentError(f"{field}.source_revision must be a full 40-character commit SHA")
        if path in seen_paths:
            raise ContentError(f"duplicate locked path: {path}")
        seen_paths.add(path)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ContentError(f"{field}.sha256 must be a lowercase SHA-256 digest")
        if entry.get("classification") != "public":
            raise ContentError(f"{field}.classification must be 'public'")
        _require_string(entry.get("license"), f"{field}.license")

    aggregate = lock.get("aggregate_sha256")
    if not isinstance(aggregate, str) or not SHA256_RE.fullmatch(aggregate):
        raise ContentError("aggregate_sha256 must be a lowercase SHA-256 digest")
    if aggregate != aggregate_sha256(files):
        raise ContentError(
            "aggregate_sha256 does not match the path-sorted 'sha256  path' file entries"
        )
    return lock


def read_lock(repository_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Return the validated single-file lock, joining shards when present.

    This does not check file bytes; verify_content does.
    """
    repository_root = Path(repository_root)
    header = content_lock.read_header(repository_root, LOCK_NAME)
    if not content_lock.is_sharded(header) and (repository_root / DEFAULT_FILE_SHARDS["directory"]).exists():
        raise ContentError(
            f"{DEFAULT_FILE_SHARDS['directory']} is present but {LOCK_NAME} "
            f"does not declare {content_lock.SHARD_KEY}"
        )
    return _validate_lock(content_lock.read_lock(repository_root, LOCK_NAME, fix_hint=LOCK_FIX_HINT))


def _check_repository_root(repository_root: Path) -> None:
    try:
        mode = repository_root.lstat().st_mode
    except OSError as error:
        raise ContentError(f"cannot inspect repository root {repository_root}: {error}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ContentError(f"repository root must be a real directory: {repository_root}")


def _list_content_files(repository_root: Path) -> set[str]:
    found: set[str] = set()
    for root_name in CONTENT_ROOTS:
        root = repository_root
        missing_root = False
        for part in root_name.split("/"):
            root = root / part
            try:
                root_mode = root.lstat().st_mode
            except FileNotFoundError:
                missing_root = True
                break
            except OSError as error:
                raise ContentError(
                    f"cannot inspect content directory {root_name}: {error}"
                ) from error
            if stat.S_ISLNK(root_mode):
                raise ContentError(f"content directory must not be a symlink: {root}")
            if not stat.S_ISDIR(root_mode):
                raise ContentError(f"content root component is not a directory: {root}")
        if missing_root:
            continue

        def walk_error(error: OSError) -> None:
            raise ContentError(f"cannot inspect content directory {root_name}: {error}") from error

        for current_dir, directory_names, file_names in os.walk(
            root, followlinks=False, onerror=walk_error
        ):
            current = Path(current_dir)
            kept_directories: list[str] = []
            for name in directory_names:
                entry = current / name
                mode = entry.lstat().st_mode
                if stat.S_ISLNK(mode):
                    relative = entry.relative_to(repository_root).as_posix()
                    raise ContentError(f"symlink directory is not allowed: {relative}")
                if not stat.S_ISDIR(mode):
                    relative = entry.relative_to(repository_root).as_posix()
                    raise ContentError(f"non-directory in content tree: {relative}")
                kept_directories.append(name)
            directory_names[:] = kept_directories

            for name in file_names:
                entry = current / name
                mode = entry.lstat().st_mode
                relative = entry.relative_to(repository_root).as_posix()
                if stat.S_ISLNK(mode):
                    raise ContentError(f"symlink file is not allowed: {relative}")
                if not stat.S_ISREG(mode):
                    raise ContentError(f"non-regular file in content tree: {relative}")
                found.add(relative)
    return found


def _tracked_text_inputs(repository_root: Path, directory: str) -> list[tuple[str, Path]]:
    """Return tracked, text-only reproduction inputs for source archives.

    Reproduction inputs are archive metadata rather than production content. A
    checked-out repository uses Git's tracked-file list so untracked evidence
    cannot silently enter a release. Recursive component staging has no Git
    directory, so it carries forward only the already-staged input tree.
    """
    input_root = repository_root / directory
    if not input_root.exists():
        return []

    if (repository_root / ".git").exists():
        try:
            output = subprocess.check_output(
                ["git", "-C", str(repository_root), "ls-files", "-z", "--", directory],
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise ContentError(f"cannot enumerate tracked {directory} files: {error}") from error
        candidates = [
            item.decode("utf-8")
            for item in output.split(b"\0")
            if item
        ]
    else:
        candidates = sorted(
            path.relative_to(repository_root).as_posix()
            for path in input_root.rglob("*")
            if path.is_file()
        )

    inputs = []
    for relative in candidates:
        path = Path(relative)
        if "__pycache__" in path.parts:
            continue
        source = _regular_file(repository_root, relative)
        try:
            source.read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContentError(f"binary reproduction file is not allowed: {relative}") from error
        inputs.append((relative, source))
    return inputs


def verify_content(repository_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Validate lock schema, file digests, and complete content-root coverage."""
    repository_root = Path(repository_root)
    _check_repository_root(repository_root)
    lock = read_lock(repository_root)
    expected_paths = {entry["path"] for entry in lock["files"]}
    actual_paths = _list_content_files(repository_root)

    missing = sorted(expected_paths - actual_paths)
    if missing:
        raise ContentError("locked file(s) are missing: " + ", ".join(missing))
    unlisted = sorted(actual_paths - expected_paths)
    if unlisted:
        raise ContentError("unlisted content file(s): " + ", ".join(unlisted))

    for entry in lock["files"]:
        path = _regular_file(repository_root, entry["path"])
        actual_digest = _sha256_file(path)
        if actual_digest != entry["sha256"]:
            raise ContentError(
                f"SHA-256 mismatch for {entry['path']}: expected {entry['sha256']}, "
                f"found {actual_digest}"
            )
    return lock


def _bundle_inputs(repository_root: Path, lock: dict[str, Any]) -> list[tuple[str, Path]]:
    inputs: dict[str, Path] = {}
    for relative in BUNDLE_METADATA:
        inputs[relative] = _regular_file(repository_root, relative)
    for entry in lock["files"]:
        relative = entry["path"]
        if relative in inputs:
            raise ContentError(f"locked content collides with bundle metadata: {relative}")
        inputs[relative] = _regular_file(repository_root, relative)
    for relative in OPTIONAL_BUNDLE_METADATA:
        candidate = repository_root / relative
        if candidate.exists() or candidate.is_symlink():
            inputs[relative] = _regular_file(repository_root, relative)
    for directory in ("release-contract", "docs", "tests"):
        base = repository_root / directory
        if base.exists():
            for candidate in sorted(base.rglob("*")):
                if candidate.suffix in (".py", ".json", ".md") and "__pycache__" not in candidate.parts:
                    relative = candidate.relative_to(repository_root).as_posix()
                    inputs[relative] = _regular_file(repository_root, relative)
    for directory in ('research', 'tests/cases'):
        for relative, source in _tracked_text_inputs(repository_root, directory):
            inputs[relative] = source
    return sorted(inputs.items())


def build_bundle(output: Path, repository_root: Path = REPOSITORY_ROOT, component: str | None = None) -> Path:
    """Write a deterministic gzip-compressed tar archive of verified source."""
    repository_root = Path(repository_root)
    lock = verify_content(repository_root)
    if component is not None:
        if component not in ('rules', 'packs'):
            raise ContentError('component must be rules or packs')
        prefixes = ('rules/', 'fixtures/policy/', 'licenses/') if component == 'rules' else ('semantic-packs/', 'fixtures/semantic/', 'scripts/upstream/', 'licenses/')
        lock = dict(lock, files=[e for e in lock['files'] if e['path'].startswith(prefixes)])
        lock['aggregate_sha256'] = aggregate_sha256(lock['files'])
    if component is not None or content_lock.is_sharded(content_lock.read_header(repository_root, LOCK_NAME)):
        # Archives carry the single-file lock, so stage it beside the inputs.
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            for relative, source in _bundle_inputs(repository_root, lock):
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            (stage / LOCK_NAME).write_bytes(lock_bytes(lock))
            return build_bundle(Path(output).absolute(), stage)
    bundle_inputs = _bundle_inputs(repository_root, lock)
    output = Path(output).expanduser()
    if not output.is_absolute():
        output = Path.cwd() / output
    if output.is_symlink():
        raise ContentError(f"bundle output must not be a symlink: {output}")
    output = output.absolute()
    try:
        output_relative = output.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError:
        output_relative = ""
    if output_relative and _is_content_path(output_relative):
        raise ContentError("bundle output must be outside locked content directories")
    input_paths = {path.absolute() for _, path in bundle_inputs}
    if output in input_paths:
        raise ContentError("bundle output would overwrite one of its source files")
    if not output.parent.is_dir():
        raise ContentError(f"bundle output directory does not exist: {output.parent}")
    if output.exists() and not output.is_file():
        raise ContentError(f"bundle output is not a regular file: {output}")

    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix=f".{output.name}.", suffix=".tmp", dir=output.parent,
            delete=False,
        ) as raw_output:
            temporary_name = raw_output.name
            with gzip.GzipFile(
                filename="", mode="wb", compresslevel=9, fileobj=raw_output, mtime=0
            ) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                    for relative, source_path in bundle_inputs:
                        info = tarfile.TarInfo(name=relative)
                        info.size = source_path.stat().st_size
                        info.mtime = 0
                        info.mode = 0o644
                        info.uid = 0
                        info.gid = 0
                        info.uname = ""
                        info.gname = ""
                        info.type = tarfile.REGTYPE
                        with source_path.open("rb") as content:
                            archive.addfile(info, content)
            raw_output.flush()
            os.fsync(raw_output.fileno())
        os.replace(temporary_name, output)
        temporary_name = None
    except OSError as error:
        raise ContentError(f"could not write bundle {output}: {error}") from error
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return output


def check_engine(engine_version: str, repository_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Verify content and require an exact, explicit engine qualification."""
    if not VERSION_RE.fullmatch(engine_version):
        raise ContentError("engine version must be a semantic version")
    lock = verify_content(repository_root)
    qualified_versions = lock["engine"]["qualified_versions"]
    if engine_version not in qualified_versions:
        recorded = ", ".join(qualified_versions) if qualified_versions else "none"
        raise ContentError(
            f"engine {engine_version} is not explicitly qualified; "
            f"engine.qualified_versions records: {recorded}. No qualification is claimed "
            f"for {engine_version}."
        )
    return lock


def _under(path: str, selectors: list[str]) -> bool:
    return any(path == selector or path.startswith(selector.rstrip("/") + "/") for selector in selectors)


def update_lock(
    repository_root: Path = REPOSITORY_ROOT,
    *,
    license_name: str | None = None,
    paths: list[str] | None = None,
) -> dict[str, list[str]]:
    """Rewrite the sharded lock from the content tree, then verify it.

    Unlisted files are added only with an explicit license, optionally limited
    to ``paths``, as public entries whose source path is their own path. A
    single-file lock is converted to DEFAULT_FILE_SHARDS.
    """
    repository_root = Path(repository_root)
    _check_repository_root(repository_root)

    def new_entry(path: str, digest: str) -> dict[str, Any] | None:
        if license_name is None or (paths and not _under(path, paths)):
            return None
        return {
            "path": path,
            "source_path": path,
            "sha256": digest,
            "classification": "public",
            "license": license_name,
        }

    changes = content_lock.update_lock(
        repository_root,
        LOCK_NAME,
        content_paths=_list_content_files(repository_root),
        new_entry=new_entry,
        default_layout=DEFAULT_FILE_SHARDS,
        validate=_validate_lock,
    )
    if not changes["unlisted"]:
        verify_content(repository_root)
    return changes


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="verify locked content and complete file coverage")
    bundle = commands.add_parser("bundle", help="write a reproducible source tar.gz bundle")
    bundle.add_argument("--output", required=True, type=Path, help="output .tar.gz path")
    bundle.add_argument("--component", choices=("rules", "packs"))
    lock = commands.add_parser(
        "lock", help="rewrite the sharded lock: add, refresh and drop entries"
    )
    lock.add_argument(
        "--license",
        help="license for new entries; without it, unlisted files are only reported",
    )
    lock.add_argument(
        "paths", nargs="*", help="limit new entries to these files or directories"
    )
    check = commands.add_parser("check", help="check content against an engine qualification")
    check.add_argument("--engine-version", required=True, help="exact engine semantic version")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "verify":
            lock = verify_content()
            print(
                f"verified {len(lock['files'])} locked file(s); "
                f"aggregate SHA-256 {lock['aggregate_sha256']}"
            )
        elif args.command == "lock":
            changes = update_lock(license_name=args.license, paths=args.paths)
            for kind in ("added", "updated", "removed"):
                for path in changes[kind]:
                    print(f"{kind}: {path}")
            if changes["unlisted"]:
                print(
                    "unlisted content file(s) need an explicit --license: "
                    + ", ".join(changes["unlisted"]),
                    file=sys.stderr,
                )
                return 1
            lock = read_lock()
            print(
                f"locked {len(lock['files'])} file(s); "
                f"aggregate SHA-256 {lock['aggregate_sha256']}"
            )
        elif args.command == "bundle":
            output = build_bundle(args.output, component=args.component)
            print(f"created reproducible source bundle: {output}")
        else:
            lock = check_engine(args.engine_version)
            print(
                f"content is explicitly qualified for engine {args.engine_version} "
                f"at {lock['engine']['qualification_revision']}"
            )
    except ContentError as error:
        print(f"content error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
