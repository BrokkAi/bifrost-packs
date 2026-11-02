#!/usr/bin/env python3
"""Verify public policy authoring identities through the production CLI."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import stat
import subprocess
import time
from typing import Any

from scripts import content

import release


class PolicyIdentityError(ValueError):
    """A source, process, or production identity contract failed."""


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_CAPTURE_BYTES = 1024 * 1024
PROCESS_TIMEOUT_SECONDS = 30.0
PROCESS_SHUTDOWN_TIMEOUT_SECONDS = 0.5
PACK_ID = "bifrost.public.rules"
IDENTITY_FORMAT = "bifrost_policy_source_identity/v1"
VERIFICATION_FORMAT = "bifrost_policy_identity_verification/v1"
PROVENANCE = {
    "source_sha256": "raw-policy-file-bytes",
    "authored_hash": "PolicyRegistry::register_policy_bytes_deferred",
    "resolved": "PolicyRegistry::register_policy_bytes",
}
# Keep this set aligned with the production built-in catalog's analyzer-free
# deferred-rejection classifier. Every other rejection is an authoring error.
SUPPORTED_WORKSPACE_DIAGNOSTIC_CODES = frozenset(
    {
        "qualified-call-locator-zero",
        "qualified-call-locator-ambiguous",
        "qualified-call-locator-partial",
        "qualified-call-locator-inactive-model",
        "qualified-call-locator-incomplete",
        "qualified-receiver-locator-zero",
        "qualified-receiver-locator-ambiguous",
        "qualified-receiver-locator-partial",
        "qualified-receiver-locator-inactive-model",
        "qualified-receiver-locator-incomplete",
        "qualified-value-locator-zero",
        "qualified-value-locator-ambiguous",
        "qualified-value-locator-partial",
        "qualified-value-locator-inactive-model",
        "qualified-value-locator-incomplete",
        "endpoint-set-import-requires-workspace",
        "declaration-selection-import-requires-workspace",
    }
)
EVIDENCE_SCOPE = "source authoring identity only; no execution or behavior qualification"
FIXED_ENVIRONMENT = {
    "BIFROST_OPEN_PACKS_DISABLE": "1",
    "BIFROST_PARALLELISM": "1",
    "BIFROST_POLICY_PARALLELISM": "1",
    "BIFROST_SQLITE_WRITER_CACHE_KIB": "524288",
    "RAYON_NUM_THREADS": "1",
    "JAVA_HOME": "",
}


def _fail(message: str) -> None:
    raise PolicyIdentityError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_cli_json(stdout: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            stdout.decode("utf-8"),
            object_pairs_hook=_json_object,
            parse_constant=lambda value: _fail(f"invalid JSON constant: {value}"),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(f"invalid CLI JSON: {error}")
    if not isinstance(value, dict):
        _fail("CLI JSON must be an object")
    return value


def _require_hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail(f"{field} must be a lowercase SHA-256 digest")
    return value


def _require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{field} must be a nonempty string")
    return value


def _exact_keys(value: Any, expected: set[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        _fail(f"{field} has unexpected or missing keys: expected {sorted(expected)}, found {actual}")
    return value


def _safe_output_name(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value)
        or value in (".", "..")
    ):
        _fail(f"unsafe {field}: {value!r}")
    return value


def _file_ref(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256(data),
        "size_bytes": len(data),
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_cli_output(
    report: dict[str, Any],
    *,
    source_id: str,
    policy_file: Path,
    source_sha256: str,
    expected_authored_hash: str,
    expected_resolved_hash: str | None,
    expected_engine_version: str,
    expected_build_identity: str,
) -> dict[str, Any]:
    _exact_keys(
        report,
        {
            "format",
            "source_id",
            "policy_file",
            "source_sha256",
            "authored_hash",
            "resolved",
            "provenance",
            "engine_version",
            "build_identity",
        },
        "CLI report",
    )
    if report["format"] != IDENTITY_FORMAT:
        _fail(f"CLI format mismatch: {report['format']!r}")
    if report["source_id"] != source_id:
        _fail(f"CLI source_id mismatch: expected {source_id!r}, found {report['source_id']!r}")
    if report["policy_file"] != str(policy_file):
        _fail(
            f"CLI policy_file mismatch: expected {str(policy_file)!r}, "
            f"found {report['policy_file']!r}"
        )
    if report["source_sha256"] != source_sha256:
        _fail(
            f"CLI source_sha256 mismatch: expected {source_sha256}, "
            f"found {report['source_sha256']!r}"
        )
    if report["engine_version"] != expected_engine_version:
        _fail(
            f"CLI engine_version mismatch: expected {expected_engine_version!r}, "
            f"found {report['engine_version']!r}"
        )
    if report["build_identity"] != expected_build_identity:
        _fail(
            f"CLI build_identity mismatch: expected {expected_build_identity!r}, "
            f"found {report['build_identity']!r}"
        )

    authored_hash = _require_hash(report["authored_hash"], "CLI authored_hash")
    if authored_hash != expected_authored_hash:
        _fail(
            f"CLI authored_hash mismatch: expected {expected_authored_hash}, "
            f"found {authored_hash}"
        )
    provenance = _exact_keys(report["provenance"], set(PROVENANCE), "CLI provenance")
    if provenance != PROVENANCE:
        _fail(f"CLI provenance mismatch: expected {PROVENANCE!r}, found {provenance!r}")

    resolved = report["resolved"]
    if not isinstance(resolved, dict) or "status" not in resolved:
        _fail("CLI resolved result must be an object with a status")
    if resolved["status"] == "available":
        _exact_keys(resolved, {"status", "semantic_hash"}, "CLI resolved available result")
        resolved_hash = _require_hash(resolved["semantic_hash"], "CLI resolved.semantic_hash")
        if expected_resolved_hash is None:
            _fail("CLI returned an available resolved hash but the manifest requires null")
        if resolved_hash != expected_resolved_hash:
            _fail(
                f"CLI resolved semantic hash mismatch: expected {expected_resolved_hash}, "
                f"found {resolved_hash}"
            )
    elif resolved["status"] == "workspace-required":
        _exact_keys(
            resolved,
            {"status", "diagnostic_code", "message"},
            "CLI workspace-required result",
        )
        diagnostic_code = _require_nonempty_string(
            resolved["diagnostic_code"], "CLI resolved.diagnostic_code"
        )
        if diagnostic_code not in SUPPORTED_WORKSPACE_DIAGNOSTIC_CODES:
            _fail(
                "CLI resolved.diagnostic_code is not a supported workspace reason: "
                f"{diagnostic_code!r}"
            )
        _require_nonempty_string(resolved["message"], "CLI resolved.message")
        if expected_resolved_hash is not None:
            _fail("CLI returned workspace-required but the manifest requires an available hash")
    else:
        _fail(f"CLI resolved status is unsupported: {resolved['status']!r}")
    return report


def _capture_process(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float = PROCESS_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    process_tree_cancellation_supported = os.name == "posix"
    if not process_tree_cancellation_supported:
        return {
            "invoked": False,
            "argv": argv,
            "cwd": str(cwd),
            "exit_code": None,
            "signal": None,
            "timed_out": False,
            "spawn_error": None,
            "unsupported_reason": "POSIX process-group cancellation is required",
            "process_tree_cancellation_supported": False,
            "capture_incomplete": False,
            "capture_errors": {},
            "stdout_overflow": False,
            "stderr_overflow": False,
            "stdout": b"",
            "stderr": b"",
        }
    try:
        process = subprocess.Popen(
            argv,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            start_new_session=True,
        )
    except OSError as error:
        return {
            "invoked": False,
            "argv": argv,
            "cwd": str(cwd),
            "exit_code": None,
            "signal": None,
            "timed_out": False,
            "spawn_error": str(error),
            "unsupported_reason": None,
            "process_tree_cancellation_supported": True,
            "capture_incomplete": False,
            "capture_errors": {},
            "stdout_overflow": False,
            "stderr_overflow": False,
            "stdout": b"",
            "stderr": b"",
        }

    assert process.stdout is not None
    assert process.stderr is not None
    stdout = bytearray()
    stderr = bytearray()
    overflow = {"stdout": False, "stderr": False}
    capture_errors: dict[str, str] = {}
    deadline = time.monotonic() + timeout_seconds
    timed_out = False
    capture_incomplete = False
    termination_requested = False
    selector = selectors.DefaultSelector()
    destinations = {"stdout": stdout, "stderr": stderr}
    streams = {"stdout": process.stdout, "stderr": process.stderr}
    open_fds: dict[int, str] = {}

    def kill_process_group() -> None:
        nonlocal capture_incomplete
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        except OSError as error:
            capture_errors["process_group_kill"] = str(error)
            capture_incomplete = True
            try:
                process.kill()
            except OSError as fallback_error:
                capture_errors["process_kill"] = str(fallback_error)
                capture_incomplete = True

    def close_fd(fd: int) -> None:
        nonlocal capture_incomplete
        name = open_fds.pop(fd, None)
        if name is None:
            return
        try:
            selector.unregister(fd)
        except KeyError:
            pass
        try:
            streams[name].close()
        except OSError as error:
            capture_errors[f"{name}_close"] = str(error)
            capture_incomplete = True

    def drain_ready(timeout: float) -> None:
        nonlocal capture_incomplete
        for selected, _ in selector.select(timeout):
            fd = selected.fd
            name = selected.data
            while True:
                try:
                    chunk = os.read(fd, 64 * 1024)
                except BlockingIOError:
                    break
                except InterruptedError:
                    continue
                except OSError as error:
                    capture_errors[name] = str(error)
                    capture_incomplete = True
                    close_fd(fd)
                    break
                if not chunk:
                    close_fd(fd)
                    break
                destination = destinations[name]
                remaining = MAX_CAPTURE_BYTES - len(destination)
                if remaining > 0:
                    destination.extend(chunk[:remaining])
                if len(chunk) > max(remaining, 0):
                    overflow[name] = True
                    break

    try:
        for name, stream in streams.items():
            fd = stream.fileno()
            os.set_blocking(fd, False)
            selector.register(fd, selectors.EVENT_READ, name)
            open_fds[fd] = name
    except OSError as error:
        capture_errors["pipe_setup"] = str(error)
        capture_incomplete = True
        termination_requested = True
        kill_process_group()

    while not termination_requested and (process.poll() is None or open_fds):
        if overflow["stdout"] or overflow["stderr"] or capture_incomplete:
            termination_requested = True
            kill_process_group()
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            termination_requested = True
            kill_process_group()
            break
        if open_fds:
            drain_ready(min(0.05, remaining))
        else:
            time.sleep(min(0.05, remaining))
        if overflow["stdout"] or overflow["stderr"] or capture_incomplete:
            termination_requested = True
            kill_process_group()

    if termination_requested:
        shutdown_deadline = time.monotonic() + PROCESS_SHUTDOWN_TIMEOUT_SECONDS
        while open_fds:
            remaining = shutdown_deadline - time.monotonic()
            if remaining <= 0:
                capture_errors["drain_timeout"] = (
                    "pipe remained open after bounded process-group cancellation"
                )
                capture_incomplete = True
                break
            drain_ready(remaining)
        if process.poll() is None:
            try:
                process.wait(timeout=max(0.0, shutdown_deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                capture_errors["process_wait"] = (
                    "process did not exit after process-group cancellation"
                )
                capture_incomplete = True
    else:
        process.wait()

    for fd in list(open_fds):
        close_fd(fd)
    selector.close()
    for stream in streams.values():
        try:
            stream.close()
        except (OSError, ValueError) as error:
            capture_errors["pipe_close"] = str(error)
            capture_incomplete = True
    process.stdout = None
    process.stderr = None
    returncode = process.returncode
    return {
        "invoked": True,
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": returncode if returncode is not None and returncode >= 0 else None,
        "signal": -returncode if returncode is not None and returncode < 0 else None,
        "timed_out": timed_out,
        "spawn_error": None,
        "unsupported_reason": None,
        "process_tree_cancellation_supported": True,
        "capture_incomplete": capture_incomplete,
        "capture_errors": dict(capture_errors),
        "stdout_overflow": overflow["stdout"],
        "stderr_overflow": overflow["stderr"],
        "stdout": bytes(stdout),
        "stderr": bytes(stderr),
    }


def _environment(output: Path) -> tuple[dict[str, str], dict[str, Any]]:
    runtime = output / ".runtime"
    cache = runtime / "cache"
    for path in (runtime, cache):
        path.mkdir(parents=True, exist_ok=True)
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("BIFROST_") and key not in {"JAVA_HOME", "RAYON_NUM_THREADS"}
    }
    env.update(FIXED_ENVIRONMENT)
    env.update(
        {
            "HOME": str(runtime),
            "XDG_CACHE_HOME": str(cache),
            "TMPDIR": str(runtime),
            "TMP": str(runtime),
            "TEMP": str(runtime),
        }
    )
    tracked = sorted(
        set(FIXED_ENVIRONMENT) | {"HOME", "XDG_CACHE_HOME", "TMPDIR", "TMP", "TEMP"}
    )
    record = {
        "variables": {name: env.get(name) for name in tracked},
        "cleared_inherited_bifrost_variables": sorted(
            name for name in os.environ if name.startswith("BIFROST_")
        ),
    }
    return env, record


def _original_manifest_resolved_hash(
    root: Path, *, content_path: str, policy_id: str
) -> str | None:
    path = PurePosixPath(content_path)
    if len(path.parts) < 3 or path.parts[0] != "rules":
        _fail(f"policy content path cannot identify its manifest: {content_path!r}")
    manifest_path = root.joinpath(*path.parts[:2], "manifest.json")
    manifest, _ = release.load_json(manifest_path)
    policies = manifest.get("policies") if isinstance(manifest, dict) else None
    if not isinstance(policies, list):
        _fail(f"policy manifest has no policies list: {manifest_path}")
    relative_policy_path = PurePosixPath(*path.parts[2:]).as_posix()
    matches = [
        policy
        for policy in policies
        if isinstance(policy, dict)
        and policy.get("id") == policy_id
        and policy.get("path") == relative_policy_path
    ]
    if len(matches) != 1:
        _fail(
            f"policy manifest entry is not unique for {policy_id}: "
            f"{manifest_path} {relative_policy_path}"
        )
    policy = matches[0]
    if "resolved_semantic_hash" not in policy:
        _fail(f"policy manifest entry is missing resolved_semantic_hash: {policy_id}")
    resolved_hash = policy["resolved_semantic_hash"]
    if resolved_hash is not None:
        _require_hash(resolved_hash, f"{policy_id} resolved_semantic_hash")
    return resolved_hash


def _validate_policy_inventory(root: Path, lock: dict[str, Any]) -> list[dict[str, Any]]:
    contents = release.public_contents(root, lock, "rules")
    policies = [item for item in contents if item.get("kind") == "policy"]
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    prepared: list[dict[str, Any]] = []
    for item in policies:
        policy_id = _safe_output_name(item.get("identity"), "policy identity")
        path = release.safe_path(item.get("path"))
        if not path.startswith("rules/"):
            _fail(f"policy content path is outside rules/: {path!r}")
        if policy_id in seen_ids:
            _fail(f"duplicate policy identity: {policy_id}")
        if path in seen_paths:
            _fail(f"duplicate policy content path: {path}")
        seen_ids.add(policy_id)
        seen_paths.add(path)
        source = root / path
        if source.is_symlink() or not source.is_file():
            _fail(f"policy source is not a regular file: {path}")
        source_bytes = source.read_bytes()
        source_sha256 = _sha256(source_bytes)
        if source_sha256 != item.get("sha256"):
            _fail(
                f"policy source SHA-256 mismatch for {path}: "
                f"expected {item.get('sha256')}, found {source_sha256}"
            )
        expected_authored_hash = _require_hash(item.get("authored_hash"), f"{policy_id} authored_hash")
        expected_resolved_hash = _original_manifest_resolved_hash(
            root, content_path=path, policy_id=policy_id
        )
        prepared.append(
            {
                "policy_id": policy_id,
                "content_path": path,
                "source_bytes": source_bytes,
                "source_sha256": source_sha256,
                "expected_authored_hash": expected_authored_hash,
                "expected_resolved_hash": expected_resolved_hash,
                "content_descriptor": item,
            }
        )
    if not policies:
        _fail("rules content contains no policies")
    return prepared


def _record_directory(output: Path, policy_id: str) -> Path:
    return output / "authoring-identities" / "public" / PACK_ID / policy_id


def _write_observation(
    *,
    directory: Path,
    output: Path,
    policy: dict[str, Any],
    binary_ref: dict[str, Any],
    profile: dict[str, Any],
    environment: dict[str, Any],
    process: dict[str, Any],
    actual: dict[str, Any] | None,
    parse_error: str | None,
    mismatch_reasons: list[str],
) -> dict[str, Any]:
    policy_path = directory / "policy.rqlp"
    stdout_path = directory / "stdout"
    stderr_path = directory / "stderr"
    policy_path.write_bytes(policy["source_bytes"])
    stdout_path.write_bytes(process["stdout"])
    stderr_path.write_bytes(process["stderr"])
    process_record = dict(process)
    process_record["stdout"] = _file_ref(stdout_path, output)
    process_record["stderr"] = _file_ref(stderr_path, output)
    _write_json(directory / "process.json", process_record)
    record = {
        "observation_kind": "policy-source-authoring-identity",
        "source": {
            "source_id": f"builtin:{PACK_ID}/{policy['content_path']}",
            "pack_id": PACK_ID,
            "policy_id": policy["policy_id"],
            "content_path": policy["content_path"],
            "content_descriptor": policy["content_descriptor"],
            "source_sha256": policy["source_sha256"],
            "expected_authored_hash": policy["expected_authored_hash"],
            "expected_resolved_semantic_hash": policy["expected_resolved_hash"],
            "retained_policy": _file_ref(policy_path, output),
        },
        "executable": binary_ref,
        "profile": profile,
        "execution_environment": environment,
        "process": process_record,
        "report": {
            "raw_stdout": _file_ref(stdout_path, output),
            "actual": actual,
            "parse_error": parse_error,
        },
        "validation": {"matches": not mismatch_reasons, "mismatch_reasons": mismatch_reasons},
        "evidence_scope": EVIDENCE_SCOPE,
    }
    _write_json(directory / "authoring-identity.json", record)
    return record


def verify_policy_identities(
    root: Path,
    binary: Path,
    output: Path,
    expected_engine_version: str,
    expected_build_identity: str,
) -> dict[str, Any]:
    """Verify every public policy's authoring identity using the production CLI.

    The result is deliberately limited to source authoring identity. It does not
    execute policies, inspect findings, or qualify behavior or workspace support.
    """
    root_arg = Path(root)
    lock = content.verify_content(root_arg)
    root_path = root_arg.resolve(strict=True)
    if not root_path.is_dir():
        _fail(f"root is not a directory: {root}")
    if not isinstance(expected_engine_version, str) or not expected_engine_version:
        _fail("expected_engine_version must be a nonempty string")
    if not isinstance(expected_build_identity, str) or not expected_build_identity:
        _fail("expected_build_identity must be a nonempty string")

    binary_arg = Path(binary)
    try:
        binary_mode = binary_arg.lstat().st_mode
    except OSError as error:
        _fail(f"cannot inspect binary {binary}: {error}")
    if stat.S_ISLNK(binary_mode) or not stat.S_ISREG(binary_mode):
        _fail(f"binary must be a regular file: {binary}")
    if not os.access(binary_arg, os.X_OK):
        _fail(f"binary is not executable: {binary}")
    binary_path = binary_arg.resolve(strict=True)
    binary_ref = {
        "path": str(binary_path),
        "sha256": _file_sha256(binary_path),
        "size_bytes": binary_path.stat().st_size,
    }

    output_arg = Path(output)
    if output_arg.is_symlink():
        _fail(f"output must not be a symlink: {output}")
    output_path = output_arg.absolute()
    output_path.mkdir(parents=True, exist_ok=True)
    if not output_path.is_dir():
        _fail(f"output must be a directory: {output}")
    output_path = output_path.resolve(strict=True)
    try:
        output_path.relative_to(root_path)
    except ValueError:
        pass
    else:
        _fail("output must be outside the source repository")

    policies = _validate_policy_inventory(root_path, lock)
    env, environment_record = _environment(output_path)
    profile = {
        "engine_version": expected_engine_version,
        "build_identity": expected_build_identity,
    }
    records: list[dict[str, Any]] = []
    for policy in policies:
        directory = _record_directory(output_path, policy["policy_id"])
        directory.mkdir(parents=True, exist_ok=True)
        policy_file = directory / "policy.rqlp"
        policy_file.write_bytes(policy["source_bytes"])
        source_id = f"builtin:{PACK_ID}/{policy['content_path']}"
        argv = [str(binary_path), "policy-source-identity", source_id, str(policy_file)]
        process = _capture_process(
            argv,
            cwd=root_path,
            env=env,
            timeout_seconds=PROCESS_TIMEOUT_SECONDS,
        )
        parse_error = None
        actual = None
        reasons: list[str] = []
        try:
            if not process["process_tree_cancellation_supported"]:
                _fail(
                    f"{policy['policy_id']}: process-tree cancellation is unsupported: "
                    f"{process['unsupported_reason']}"
                )
            if not process["invoked"]:
                _fail(f"{policy['policy_id']}: could not invoke production CLI: {process['spawn_error']}")
            if process["stdout_overflow"] or process["stderr_overflow"]:
                _fail(f"{policy['policy_id']}: CLI output exceeded the bounded capture size")
            if process["capture_incomplete"]:
                _fail(
                    f"{policy['policy_id']}: CLI output capture was incomplete: "
                    f"{process['capture_errors']}"
                )
            if process["timed_out"]:
                _fail(f"{policy['policy_id']}: CLI timed out")
            if process["signal"] is not None:
                _fail(f"{policy['policy_id']}: CLI terminated by signal {process['signal']}")
            if process["exit_code"] != 0:
                _fail(f"{policy['policy_id']}: CLI exited with status {process['exit_code']}")
            try:
                actual = _parse_cli_json(process["stdout"])
            except PolicyIdentityError as error:
                parse_error = str(error)
                raise
            _validate_cli_output(
                actual,
                source_id=source_id,
                policy_file=policy_file,
                source_sha256=policy["source_sha256"],
                expected_authored_hash=policy["expected_authored_hash"],
                expected_resolved_hash=policy["expected_resolved_hash"],
                expected_engine_version=expected_engine_version,
                expected_build_identity=expected_build_identity,
            )
        except PolicyIdentityError as error:
            message = str(error)
            if message.startswith("invalid CLI JSON") or message.startswith("CLI JSON must"):
                parse_error = message
            reasons.append(message)
            _write_observation(
                directory=directory,
                output=output_path,
                policy=policy,
                binary_ref=binary_ref,
                profile=profile,
                environment=environment_record,
                process=process,
                actual=actual,
                parse_error=parse_error,
                mismatch_reasons=reasons,
            )
            raise
        record = _write_observation(
            directory=directory,
            output=output_path,
            policy=policy,
            binary_ref=binary_ref,
            profile=profile,
            environment=environment_record,
            process=process,
            actual=actual,
            parse_error=None,
            mismatch_reasons=[],
        )
        records.append(record)

    result = {
        "format": VERIFICATION_FORMAT,
        "binary": binary_ref,
        "profile": profile,
        "execution_environment": environment_record,
        "policies": records,
        "evidence_scope": EVIDENCE_SCOPE,
    }
    _write_json(output_path / "verification.json", result)
    return result
