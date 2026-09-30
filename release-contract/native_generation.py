#!/usr/bin/env python3
"""Generate and qualify the byte reproducibility of a native pack bundle.

Configuration paths are root-relative. A recipe is invoked as
``bash SCRIPT OUTPUT_PART WORK_DIR`` and receives the pinned executable in
``BIFROST_SEMANTIC_PACK_BIN``. Recipes should use that executable for native
generation. Direct ``jobs`` invoke its ``generate`` command themselves.

This runner verifies native bundle integrity and repeatability. It does not
establish consumer compatibility or semantic completeness.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


class NativeGenerationError(ValueError):
    """A configuration, integrity, execution, or reproducibility failure."""


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
SEMVER_RE = re.compile(
    r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
GENERATOR_FIELDS = {
    "version",
    "binary_sha256",
    "repository",
    "commit",
    "asset",
    "asset_sha256",
}
BUILD_FIELDS = {"rust_toolchain", "cargo_lock_sha256"}
BUILD_RECEIPT_FIELDS = {
    "schema_version", "generator_commit", "source_archive_sha256",
    "cargo_lock_sha256", "rust_toolchain", "binary_sha256",
}


def _fail(message: str) -> None:
    raise NativeGenerationError(message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(data: bytes, description: str) -> Any:
    try:
        return json.loads(data, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(f"invalid JSON in {description}: {error}")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_root_path(root: Path, raw: Any, description: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        _fail(f"{description} must be a nonempty root-relative path")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        _fail(f"unsafe {description} path: {raw!r}")
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        try:
            mode = candidate.lstat().st_mode
        except OSError as error:
            _fail(f"cannot inspect {description} {raw!r}: {error}")
        if stat.S_ISLNK(mode):
            _fail(f"symlink in {description} path: {raw!r}")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail(f"{description} escapes repository root: {raw!r}")
    return resolved


def _validate_name(value: Any, description: str) -> str:
    if not isinstance(value, str) or not NAME_RE.fullmatch(value) or value in (".", ".."):
        _fail(f"{description} must be a simple filename-safe name")
    return value


def _validate_sha(value: Any, description: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(f"{description} must be a lowercase SHA-256 digest")
    return value


def _file_or_tree_sha256(path: Path) -> tuple[str, str]:
    """Hash a regular file or a deterministic tree, rejecting links/special files."""
    mode = path.lstat().st_mode
    if stat.S_ISREG(mode):
        return "file", _sha256_file(path)
    if not stat.S_ISDIR(mode):
        _fail(f"input is not a regular file or directory: {path}")

    digest = hashlib.sha256()
    entries: list[tuple[str, Path, bool]] = []
    for directory, dirnames, filenames in os.walk(path, topdown=True, followlinks=False):
        directory_path = Path(directory)
        dirnames.sort()
        filenames.sort()
        for name in list(dirnames):
            entry = directory_path / name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                _fail(f"symlink or special file in input tree: {entry}")
            entries.append((entry.relative_to(path).as_posix(), entry, True))
        for name in filenames:
            entry = directory_path / name
            mode = entry.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                _fail(f"symlink or special file in input tree: {entry}")
            entries.append((entry.relative_to(path).as_posix(), entry, False))

    for relative, entry, is_directory in sorted(entries, key=lambda row: row[0]):
        encoded = relative.encode("utf-8")
        digest.update(b"D" if is_directory else b"F")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        if not is_directory:
            size = entry.stat().st_size
            digest.update(size.to_bytes(8, "big"))
            with entry.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
    return "tree", digest.hexdigest()


def _validate_config(root: Path, config_path: Path) -> tuple[dict[str, Any], bytes, list[dict[str, Any]], list[dict[str, Any]]]:
    config_path = config_path.resolve(strict=True)
    try:
        config_path.relative_to(root)
    except ValueError:
        _fail("config must be inside repository root")
    config_bytes = config_path.read_bytes()
    config = _load_json(config_bytes, str(config_path))
    if not isinstance(config, dict) or set(config) - {"schema_version", "generator", "jobs", "recipes"}:
        _fail("config must contain only schema_version, generator, jobs, and recipes")
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        _fail("unsupported native generation config schema_version (expected 1)")

    generator = config.get("generator")
    if not isinstance(generator, dict) or set(generator) not in (GENERATOR_FIELDS, GENERATOR_FIELDS | {"build"}):
        _fail("generator must contain the six generator pins and only optional build metadata")
    if not isinstance(generator["version"], str) or not SEMVER_RE.fullmatch(generator["version"]):
        _fail("generator.version must be a semantic version without a leading v")
    if "build" in generator:
        build = generator["build"]
        if not isinstance(build, dict) or set(build) != BUILD_FIELDS:
            _fail("generator.build must contain exactly rust_toolchain and cargo_lock_sha256")
        if not isinstance(build["rust_toolchain"], str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", build["rust_toolchain"]):
            _fail("generator.build.rust_toolchain must be an exact numeric toolchain version")
        _validate_sha(build["cargo_lock_sha256"], "generator.build.cargo_lock_sha256")
    if generator["binary_sha256"] is not None:
        _validate_sha(generator["binary_sha256"], "generator.binary_sha256")
    elif "build" not in generator:
        _fail("generator.binary_sha256 may be null only with validated build metadata")
    _validate_sha(generator["asset_sha256"], "generator.asset_sha256")
    if not isinstance(generator["repository"], str) or not generator["repository"].strip():
        _fail("generator.repository must be nonempty")
    if not isinstance(generator["commit"], str) or not COMMIT_RE.fullmatch(generator["commit"]):
        _fail("generator.commit must be a full 40- or 64-character commit id")
    if not isinstance(generator["asset"], str) or not generator["asset"].strip():
        _fail("generator.asset must be nonempty")

    jobs_raw = config.get("jobs", [])
    recipes_raw = config.get("recipes", [])
    if not isinstance(jobs_raw, list) or not isinstance(recipes_raw, list):
        _fail("jobs and recipes must be arrays")
    if not jobs_raw and not recipes_raw:
        _fail("generation plan is empty; configure at least one job or recipe")

    jobs: list[dict[str, Any]] = []
    recipes: list[dict[str, Any]] = []
    names: set[str] = set()
    for row in jobs_raw:
        if not isinstance(row, dict) or set(row) != {"name", "spec", "artifact"}:
            _fail("each job must contain exactly name, spec, and artifact")
        name = _validate_name(row["name"], "job.name")
        if name in names:
            _fail(f"duplicate generation plan name: {name}")
        names.add(name)
        spec = _safe_root_path(root, row["spec"], f"job {name} spec")
        artifact = _safe_root_path(root, row["artifact"], f"job {name} artifact")
        for description, path in (("spec", spec), ("artifact", artifact)):
            mode = path.lstat().st_mode
            if description == "spec" and not stat.S_ISREG(mode):
                _fail(f"job {name} spec must be a regular file")
            if description == "artifact" and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                _fail(f"job {name} artifact must be a regular file or directory")
        _file_or_tree_sha256(artifact)
        jobs.append({"name": name, "spec": row["spec"], "spec_path": spec,
                     "artifact": row["artifact"], "artifact_path": artifact})

    for row in recipes_raw:
        if not isinstance(row, dict) or set(row) != {"name", "script"}:
            _fail("each recipe must contain exactly name and script")
        name = _validate_name(row["name"], "recipe.name")
        if name in names:
            _fail(f"duplicate generation plan name: {name}")
        names.add(name)
        script = _safe_root_path(root, row["script"], f"recipe {name} script")
        if not stat.S_ISREG(script.lstat().st_mode):
            _fail(f"recipe {name} script must be a regular file")
        recipes.append({"name": name, "script": row["script"], "script_path": script})

    return generator, config_bytes, jobs, recipes


def _validate_build_attestation(
    generator: dict[str, Any], attestation: Any, actual_binary_sha: str
) -> dict[str, Any]:
    """Bind a workflow build attestation to the configured source and executable."""
    if "build" not in generator:
        _fail("prebuilt generator does not permit a build receipt")
    if not isinstance(attestation, dict) or set(attestation) != BUILD_RECEIPT_FIELDS:
        _fail("build receipt must contain exactly the six build attestation fields")
    if type(attestation["schema_version"]) is not int or attestation["schema_version"] != 1:
        _fail("unsupported build receipt schema_version (expected 1)")
    expected = {
        "generator_commit": generator["commit"],
        "source_archive_sha256": generator["asset_sha256"],
        "cargo_lock_sha256": generator["build"]["cargo_lock_sha256"],
        "rust_toolchain": generator["build"]["rust_toolchain"],
        "binary_sha256": actual_binary_sha,
    }
    for field, value in expected.items():
        if attestation[field] != value:
            _fail(f"build receipt {field} mismatch")
    return attestation


def _input_plan_record(jobs: list[dict[str, Any]], recipes: list[dict[str, Any]]) -> dict[str, Any]:
    job_records = []
    for job in jobs:
        _, spec_hash = _file_or_tree_sha256(job["spec_path"])
        artifact_kind, artifact_hash = _file_or_tree_sha256(job["artifact_path"])
        job_records.append({
            "name": job["name"],
            "spec": job["spec"],
            "spec_sha256": spec_hash,
            "artifact": job["artifact"],
            "artifact_kind": artifact_kind,
            "artifact_sha256": artifact_hash,
        })
    recipe_records = []
    for recipe in recipes:
        recipe_records.append({
            "name": recipe["name"],
            "script": recipe["script"],
            "script_sha256": _sha256_file(recipe["script_path"]),
        })
    return {"jobs": job_records, "recipes": recipe_records}


def _run_command(command: list[str], *, cwd: Path, env: dict[str, str], purpose: str) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        details = (result.stderr or result.stdout).strip()
        if len(details) > 4000:
            details = details[-4000:]
        suffix = f": {details}" if details else ""
        _fail(f"{purpose} failed with exit status {result.returncode}{suffix}")


def _bundle_files(bundle: Path) -> dict[str, Path]:
    if not bundle.is_dir() or bundle.is_symlink():
        _fail(f"native tool did not produce a bundle directory: {bundle}")
    files: dict[str, Path] = {}
    for directory, dirnames, filenames in os.walk(bundle, topdown=True, followlinks=False):
        directory_path = Path(directory)
        dirnames.sort()
        filenames.sort()
        for dirname in dirnames:
            path = directory_path / dirname
            if path.is_symlink() or not path.is_dir():
                _fail(f"symlink or special directory in native bundle: {path}")
        for filename in filenames:
            path = directory_path / filename
            if path.is_symlink() or not path.is_file():
                _fail(f"symlink or special file in native bundle: {path}")
            files[path.relative_to(bundle).as_posix()] = path
    return files


def _inspect_bundle(bundle: Path, binary: Path, expected_version: str, *, cwd: Path, env: dict[str, str]) -> tuple[dict[str, Path], bytes, str]:
    _bundle_files(bundle)
    _run_command([str(binary), "verify", str(bundle)], cwd=cwd, env=env, purpose=f"verify {bundle}")
    files = _bundle_files(bundle)
    index_path = files.get("index.json")
    if index_path is None:
        _fail(f"verified native bundle is missing index.json: {bundle}")
    index = _load_json(index_path.read_bytes(), str(index_path))
    if not isinstance(index, dict) or type(index.get("schema_version")) is not int or index["schema_version"] != 3:
        _fail(f"native bundle has unsupported index schema: {bundle}")
    generator = index.get("generator")
    if not isinstance(generator, dict) or generator.get("version") != expected_version:
        found = generator.get("version") if isinstance(generator, dict) else None
        _fail(f"native bundle generator version mismatch: expected {expected_version}, found {found}")
    packs = index.get("packs")
    productions = index.get("generated_productions", [])
    if not isinstance(packs, list) or not isinstance(productions, list) or not (packs or productions):
        _fail(f"native bundle contains no packs or generated productions: {bundle}")
    measurements_path = files.get("measurements.json")
    if measurements_path is None:
        _fail(f"verified native bundle is missing measurements.json: {bundle}")
    measurements = measurements_path.read_bytes()
    _load_json(measurements, str(measurements_path))
    content_digest = hashlib.sha256()
    for relative, path in sorted(files.items()):
        if relative == "measurements.json":
            continue
        name = relative.encode("utf-8")
        data_size = path.stat().st_size
        content_digest.update(len(name).to_bytes(8, "big"))
        content_digest.update(name)
        content_digest.update(data_size.to_bytes(8, "big"))
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                content_digest.update(chunk)
    return files, measurements, content_digest.hexdigest()


def _run_plan(
    run_root: Path,
    *,
    root: Path,
    binary: Path,
    generator_version: str,
    jobs: list[dict[str, Any]],
    recipes: list[dict[str, Any]],
    env: dict[str, str],
) -> tuple[Path, dict[str, Path], bytes, str]:
    run_root.mkdir()
    outputs_root = run_root / "outputs"
    work_root = run_root / "work"
    outputs_root.mkdir()
    work_root.mkdir()
    bundle_paths: list[Path] = []

    for job in jobs:
        output = outputs_root / job["name"]
        command = [str(binary), "generate", str(output), str(job["spec_path"]), str(job["artifact_path"])]
        _run_command(command, cwd=root, env=env, purpose=f"generate job {job['name']}")
        _inspect_bundle(output, binary, generator_version, cwd=root, env=env)
        bundle_paths.append(output)

    for recipe in recipes:
        output = outputs_root / recipe["name"]
        work = work_root / recipe["name"]
        work.mkdir()
        _run_command(
            ["bash", str(recipe["script_path"]), str(output), str(work)],
            cwd=root,
            env=env,
            purpose=f"run recipe {recipe['name']}",
        )
        _inspect_bundle(output, binary, generator_version, cwd=root, env=env)
        bundle_paths.append(output)

    merged = run_root / "merged"
    command = [str(binary), "merge", str(merged), *(str(path) for path in bundle_paths)]
    _run_command(command, cwd=root, env=env, purpose="merge native bundles")
    files, measurements, content_sha = _inspect_bundle(
        merged, binary, generator_version, cwd=root, env=env
    )
    return merged, files, measurements, content_sha


def _source_provenance(root: Path) -> dict[str, str | None]:
    try:
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
            text=True,
            stderr=subprocess.PIPE,
        )
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        _fail(f"cannot record clean repository source provenance: {error}")
    if status:
        _fail("repository source must be clean before native generation")
    if not COMMIT_RE.fullmatch(commit):
        _fail("git returned an invalid repository source commit")
    try:
        repository = subprocess.check_output(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError:
        repository = None
    return {"repository": repository, "commit": commit}


def _assert_source_unchanged(root: Path, expected_commit: str) -> None:
    try:
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
            text=True,
            stderr=subprocess.PIPE,
        )
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        _fail(f"cannot recheck repository source provenance: {error}")
    if commit != expected_commit:
        _fail("repository HEAD changed during native generation")
    if status:
        _fail("repository source became dirty during native generation")


def _write_deterministic_archive(bundle: Path, files: dict[str, Path], destination: Path) -> None:
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                root_info = tarfile.TarInfo("bifrost-semantic-packs/")
                root_info.type = tarfile.DIRTYPE
                root_info.mode = 0o755
                root_info.mtime = 0
                root_info.uid = root_info.gid = 0
                root_info.uname = root_info.gname = ""
                archive.addfile(root_info)
                directories: set[str] = set()
                for relative in files:
                    parent = PurePosixPath(relative).parent
                    while parent.as_posix() not in (".", ""):
                        directories.add(parent.as_posix())
                        parent = parent.parent
                for directory in sorted(directories):
                    info = tarfile.TarInfo(f"bifrost-semantic-packs/{directory}/")
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    archive.addfile(info)
                for relative, source in sorted(files.items()):
                    info = tarfile.TarInfo(f"bifrost-semantic-packs/{relative}")
                    info.size = source.stat().st_size
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with source.open("rb") as content:
                        archive.addfile(info, content)


def run(
    root: Path, config: Path, binary: Path, output: Path,
    build_receipt: Path | None = None,
) -> dict[str, Any]:
    """Run a two-pass native generation and publish archive plus receipt.

    ``output`` is a new directory outside ``root``. It receives native.tar.gz,
    generation.json, and the exact measurements bytes from both passes under
    ``measurements/run-N.json``.
    """
    root = root.resolve(strict=True)
    if not root.is_dir():
        _fail("--root must name a directory")
    config_path = config if config.is_absolute() else root / config
    generator, config_bytes, jobs, recipes = _validate_config(root, config_path)
    binary_path = binary.resolve(strict=True)
    if not binary_path.is_file() or not os.access(binary_path, os.X_OK):
        _fail("--binary must name an executable regular file")
    actual_binary_sha = _sha256_file(binary_path)
    if generator["binary_sha256"] is not None and actual_binary_sha != generator["binary_sha256"]:
        _fail(
            "native generator binary checksum mismatch: "
            f"expected {generator['binary_sha256']}, found {actual_binary_sha}"
        )

    generator_build = None
    build_receipt_path = None
    build_receipt_sha = None
    if "build" in generator:
        if build_receipt is None:
            _fail("source-built generator requires --build-receipt; no prebuilt fallback")
        if build_receipt.is_symlink() or not build_receipt.is_file():
            _fail("--build-receipt must name a regular file without a symlink")
        build_receipt_path = build_receipt.resolve(strict=True)
        build_receipt_bytes = build_receipt_path.read_bytes()
        generator_build = _validate_build_attestation(
            generator, _load_json(build_receipt_bytes, str(build_receipt_path)), actual_binary_sha
        )
        build_receipt_sha = _sha256_bytes(build_receipt_bytes)
    elif build_receipt is not None:
        _fail("prebuilt generator does not permit a build receipt")

    output_arg = output if output.is_absolute() else Path.cwd() / output
    if output_arg.name in ("", ".", ".."):
        _fail("--output must name a new directory")
    parent_arg = output_arg.parent
    if not parent_arg.exists() or not parent_arg.is_dir():
        _fail("--output parent directory must already exist")
    final_output = parent_arg.resolve(strict=True) / output_arg.name
    try:
        final_output.relative_to(root)
    except ValueError:
        pass
    else:
        _fail("--output must be outside repository root")
    if final_output.exists() or final_output.is_symlink():
        _fail(f"--output already exists: {final_output}")

    initial_plan = _input_plan_record(jobs, recipes)
    plan_bytes = json.dumps(initial_plan, sort_keys=True, separators=(",", ":")).encode()
    plan_sha = _sha256_bytes(plan_bytes)
    config_sha = _sha256_bytes(config_bytes)
    source = _source_provenance(root)

    def ensure_inputs_unchanged() -> None:
        _assert_source_unchanged(root, source["commit"])
        if _sha256_file(config_path) != config_sha:
            _fail("generation config changed during execution")
        if _sha256_file(binary_path) != actual_binary_sha:
            _fail("native generator binary changed during execution")
        if build_receipt_path is not None and _sha256_file(build_receipt_path) != build_receipt_sha:
            _fail("generator build receipt changed during execution")
        current_plan = _input_plan_record(jobs, recipes)
        current_bytes = json.dumps(current_plan, sort_keys=True, separators=(",", ":")).encode()
        if _sha256_bytes(current_bytes) != plan_sha:
            _fail("generation recipe, spec, or artifact changed during execution")

    with tempfile.TemporaryDirectory(prefix=".native-generation-", dir=final_output.parent) as temporary:
        temp_root = Path(temporary)
        source_cache = temp_root / "source-cache"
        source_cache.mkdir()
        env = os.environ.copy()
        env["BIFROST_SEMANTIC_PACK_BIN"] = str(binary_path)
        env["SEMANTIC_PACK_SOURCE_CACHE"] = str(source_cache)
        run_results: list[dict[str, Any]] = []
        run_data: list[tuple[Path, dict[str, Path], bytes]] = []
        for run_id in ("run-1", "run-2"):
            ensure_inputs_unchanged()
            merged, files, measurements, content_sha = _run_plan(
                temp_root / run_id,
                root=root,
                binary=binary_path,
                generator_version=generator["version"],
                jobs=jobs,
                recipes=recipes,
                env=env,
            )
            ensure_inputs_unchanged()
            run_results.append({
                "id": run_id,
                "native_content_sha256": content_sha,
                "measurements_sha256": _sha256_bytes(measurements),
            })
            run_data.append((merged, files, measurements))

        first_content = run_results[0]["native_content_sha256"]
        second_content = run_results[1]["native_content_sha256"]
        if first_content != second_content:
            first_files = set(run_data[0][1]) - {"measurements.json"}
            second_files = set(run_data[1][1]) - {"measurements.json"}
            differing = sorted(
                path for path in first_files | second_files
                if path not in first_files or path not in second_files
                or _sha256_file(run_data[0][1][path]) != _sha256_file(run_data[1][1][path])
            )
            _fail("native content is not reproducible; differing files: " + ", ".join(differing[:20]))

        ensure_inputs_unchanged()
        stage = temp_root / "package"
        stage.mkdir()
        measurements_dir = stage / "measurements"
        measurements_dir.mkdir()
        for run_id, (_, _, measurements) in zip(("run-1", "run-2"), run_data):
            (measurements_dir / f"{run_id}.json").write_bytes(measurements)

        first_files = run_data[0][1]
        archive_path = stage / "native.tar.gz"
        _write_deterministic_archive(run_data[0][0], first_files, archive_path)
        archive_sha = _sha256_file(archive_path)
        receipt: dict[str, Any] = {
            "schema_version": 1,
            "source": source,
            "config_sha256": config_sha,
            "plan_sha256": plan_sha,
            "plan": initial_plan,
            "generator": generator,
            "generator_build": generator_build,
            "binary_sha256": actual_binary_sha,
            "archive": {"path": "native.tar.gz", "sha256": archive_sha},
            "reproducibility": {
                "status": "byte-identical-native-content",
                "excluded_from_comparison": ["measurements.json"],
                "native_content_sha256": first_content,
                "measurement_records": [
                    {
                        "run": run_id,
                        "path": f"measurements/{run_id}.json",
                        "sha256": run_results[index]["measurements_sha256"],
                        "included_in_archive": index == 0,
                    }
                    for index, run_id in enumerate(("run-1", "run-2"))
                ],
                "runs": run_results,
            },
            "qualification": {
                "status": "pending",
                "code": "native-generation-only",
                "semantic_completeness": "not-qualified",
                "consumer_compatibility": "not-qualified",
            },
        }
        (stage / "generation.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if final_output.exists() or final_output.is_symlink():
            _fail(f"--output appeared during generation: {final_output}")
        os.replace(stage, final_output)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, help="required attestation for a source-built generator")
    parser.add_argument("--output", type=Path, required=True, help="new output directory outside --root")
    args = parser.parse_args(argv)
    try:
        result = run(args.root, args.config, args.binary, args.output, args.build_receipt)
    except (NativeGenerationError, OSError, subprocess.SubprocessError) as error:
        print(f"native generation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"output": str(args.output), "archive": result["archive"],
                      "qualification": result["qualification"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
