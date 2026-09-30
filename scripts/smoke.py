#!/usr/bin/env python3
"""Run a bounded positive/near-miss smoke for one explicit Python policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path("rules/bifrost.code-smells/policies/dynamic-evaluation.rqlp")
MANIFEST_PATH = Path("rules/bifrost.code-smells/manifest.json")
POLICY_ID = "bifrost.correctness.dynamic-evaluation"
CASE_PATHS = {
    "positive": Path("tests/cases/dynamic-evaluation/positive.py"),
    "near-miss": Path("tests/cases/dynamic-evaluation/near-miss.py"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_RE = re.compile(r"\bbifrost\s+([^\s]+)", re.IGNORECASE)
MAX_TIMEOUT_SECONDS = 600


class SmokeError(Exception):
    """The engine or its report failed the focused smoke contract."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _load_policy_authored_hash(repository_root: Path) -> str:
    try:
        manifest = json.loads((repository_root / MANIFEST_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SmokeError(f"cannot read policy manifest {MANIFEST_PATH}: {error}") from error
    matches = [
        item
        for item in manifest.get("policies", [])
        if item.get("path") == POLICY_PATH.relative_to("rules/bifrost.code-smells").as_posix()
        and item.get("id") == POLICY_ID
    ]
    if len(matches) != 1:
        raise SmokeError(
            f"manifest must contain exactly one entry for {POLICY_ID} at {POLICY_PATH}"
        )
    authored_hash = matches[0].get("authored_hash")
    if not isinstance(authored_hash, str) or not SHA256_RE.fullmatch(authored_hash):
        raise SmokeError(f"manifest authored_hash for {POLICY_ID} is invalid")
    return authored_hash


def _decode_capture(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _run_version(binary: Path, timeout: int, environment: dict[str, str]) -> tuple[str, str, str]:
    try:
        completed = subprocess.run(
            [str(binary), "--version"],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SmokeError(f"could not capture {binary} --version: {error}") from error
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise SmokeError(f"{binary} --version exited {completed.returncode}: {output.strip()}")
    match = VERSION_RE.search(output)
    if not match:
        raise SmokeError(f"could not parse a Bifrost version from --version output: {output.strip()}")
    return match.group(1), completed.stdout, completed.stderr


def _read_raw_report(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SmokeError(f"engine did not write the requested raw report: {path}") from error
    except (OSError, json.JSONDecodeError) as error:
        raise SmokeError(f"raw report is unreadable or malformed at {path}: {error}") from error
    if not isinstance(report, dict):
        raise SmokeError("raw report must be a JSON object")
    return report


def _validate_report(
    report: dict[str, Any], case_name: str, returncode: int, authored_hash: str
) -> dict[str, Any]:
    rules = report.get("rules")
    if not isinstance(rules, list):
        raise SmokeError(f"{case_name}: raw report has no rules array")
    selected_rules = [rule for rule in rules if isinstance(rule, dict) and rule.get("policy_id") == POLICY_ID]
    if len(selected_rules) != 1 or selected_rules[0].get("policy_hash") != authored_hash:
        raise SmokeError(f"{case_name}: raw report does not contain the expected authored policy hash")

    runs = report.get("runs")
    if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
        raise SmokeError(f"{case_name}: expected exactly one explicit policy run")
    run = runs[0]
    if run.get("policy_id") != POLICY_ID or run.get("policy_hash") != authored_hash:
        raise SmokeError(f"{case_name}: run does not match the requested policy and authored hash")
    completion = run.get("completion")
    if not isinstance(completion, dict) or completion.get("type") != "complete":
        actual = completion.get("type") if isinstance(completion, dict) else completion
        raise SmokeError(f"{case_name}: report is incomplete (completion={actual!r})")

    for source, owner in ((report.get("diagnostics"), "report"), (run.get("diagnostics"), "run")):
        if not isinstance(source, list):
            raise SmokeError(f"{case_name}: {owner} has no diagnostics array")
        if source:
            raise SmokeError(f"{case_name}: {owner} contains diagnostics; smoke is not cleanly complete")

    findings = run.get("findings")
    if not isinstance(findings, list):
        raise SmokeError(f"{case_name}: raw report has no findings array")
    unexpected = [
        finding
        for finding in findings
        if not isinstance(finding, dict) or finding.get("policy_id") != POLICY_ID
    ]
    if unexpected:
        raise SmokeError(f"{case_name}: report contains findings outside {POLICY_ID}")

    expected_count = 1 if case_name == "positive" else 0
    if len(findings) != expected_count:
        raise SmokeError(
            f"{case_name}: expected {expected_count} finding(s), found {len(findings)}"
        )
    expected_exit = 1 if expected_count else 0
    if returncode != expected_exit:
        raise SmokeError(
            f"{case_name}: expected engine exit {expected_exit} for {expected_count} finding(s), "
            f"got {returncode}"
        )
    concise_findings = [
        {
            "id": finding.get("id"),
            "policy_id": finding.get("policy_id"),
            "policy_hash": finding.get("policy_hash"),
            "primary": finding.get("primary"),
        }
        for finding in findings
    ]
    return {
        "completion": completion,
        "finding_count": len(findings),
        "findings": concise_findings,
        "reported_policy_hash": run["policy_hash"],
    }


def _prepare_output(output: Path) -> Path:
    output = output.expanduser()
    if not output.is_absolute():
        output = Path.cwd() / output
    output = output.absolute()
    if output.is_symlink():
        raise SmokeError(f"output directory must not be a symlink: {output}")
    if output.exists():
        if not output.is_dir():
            raise SmokeError(f"output path is not a directory: {output}")
        if any(output.iterdir()):
            raise SmokeError(f"output directory must be empty: {output}")
    else:
        output.mkdir(parents=True)
    return output


def run_smoke(binary: Path, output: Path, timeout: int = 120,
              repository_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    """Run two isolated cases and save immutable inputs and per-run evidence."""
    if timeout < 1 or timeout > MAX_TIMEOUT_SECONDS:
        raise SmokeError(f"timeout must be between 1 and {MAX_TIMEOUT_SECONDS} seconds")
    repository_root = Path(repository_root).resolve()
    try:
        binary = Path(binary).expanduser().resolve(strict=True)
        mode = binary.stat().st_mode
    except OSError as error:
        raise SmokeError(f"cannot inspect engine binary: {error}") from error
    if not stat.S_ISREG(mode) or not os.access(binary, os.X_OK):
        raise SmokeError(f"engine binary is not an executable regular file: {binary}")

    output = _prepare_output(Path(output))
    policy = repository_root / POLICY_PATH
    authored_hash = _load_policy_authored_hash(repository_root)
    try:
        policy_bytes = policy.read_bytes()
        fixtures = {name: (repository_root / path).read_bytes() for name, path in CASE_PATHS.items()}
    except OSError as error:
        raise SmokeError(f"cannot read focused smoke inputs: {error}") from error

    input_dir = output / "inputs"
    input_dir.mkdir()
    copied_policy = input_dir / "dynamic-evaluation.rqlp"
    copied_policy.write_bytes(policy_bytes)
    for name, contents in fixtures.items():
        destination = input_dir / f"{name}.py"
        destination.write_bytes(contents)

    environment = os.environ.copy()
    environment["JAVA_HOME"] = ""
    environment["BIFROST_SEMANTIC_PACK_DOWNLOAD"] = "off"
    engine_version, version_stdout, version_stderr = _run_version(binary, timeout, environment)
    (output / "version.stdout.txt").write_text(version_stdout, encoding="utf-8")
    (output / "version.stderr.txt").write_text(version_stderr, encoding="utf-8")
    summary: dict[str, Any] = {
        "schema_version": 1,
        "scope": "one explicit Python structural dynamic-evaluation policy; this smoke does not qualify the full copied content set",
        "engine_version": engine_version,
        "engine_version_output": {"stdout": version_stdout, "stderr": version_stderr},
        "binary_path": str(binary),
        "binary_sha256": _sha256_file(binary),
        "policy_id": POLICY_ID,
        "policy_path": POLICY_PATH.as_posix(),
        "policy_authored_hash": authored_hash,
        "copied_policy_sha256": hashlib.sha256(policy_bytes).hexdigest(),
        "copied_policy_path": "inputs/dynamic-evaluation.rqlp",
        "fixture_hashes": {
            name: hashlib.sha256(contents).hexdigest() for name, contents in fixtures.items()
        },
        "environment": {
            "JAVA_HOME": "",
            "BIFROST_SEMANTIC_PACK_DOWNLOAD": "off",
        },
        "expected": {
            "positive": {"completion": "complete", "finding_count": 1, "exit_code": 1},
            "near-miss": {"completion": "complete", "finding_count": 0, "exit_code": 0},
        },
        "runs": [],
        "qualification": "focused smoke only; no whole-copy or release qualification",
    }
    _write_json(output / "smoke.json", summary)

    try:
        for case_name in CASE_PATHS:
            run_dir = output / "runs" / case_name
            run_dir.mkdir(parents=True)
            workspace = Path(tempfile.mkdtemp(prefix=f"bifrost-smoke-{case_name}-"))
            run_record: dict[str, Any] = {
                "case": case_name,
                "fixture_sha256": summary["fixture_hashes"][case_name],
                "policy_authored_hash": authored_hash,
                "copied_policy_sha256": summary["copied_policy_sha256"],
                "raw_report": f"runs/{case_name}/raw-report.json",
                "stdout": f"runs/{case_name}/stdout.txt",
                "stderr": f"runs/{case_name}/stderr.txt",
                "completion": None,
                "finding_count": None,
                "exit_code": None,
                "status": "running",
            }
            summary["runs"].append(run_record)
            try:
                workspace_policy = workspace / "dynamic-evaluation.rqlp"
                workspace_fixture = workspace / "case.py"
                workspace_policy.write_bytes(policy_bytes)
                workspace_fixture.write_bytes(fixtures[case_name])
                raw_report_path = (run_dir / "raw-report.json").resolve()
                command = [
                    str(binary),
                    "--root", str(workspace),
                    "--no-builtin-policies",
                    "--policy-file", workspace_policy.name,
                    "--format", "json",
                    "--fail-on", "finding",
                    "--output", str(raw_report_path),
                ]
                run_record["command"] = command
                completed = subprocess.run(
                    command,
                    cwd=workspace,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                    shell=False,
                )
                (run_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
                (run_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
                run_record["exit_code"] = completed.returncode
                report = _read_raw_report(raw_report_path)
                run_record["raw_report_sha256"] = _sha256_file(raw_report_path)
                checked = _validate_report(
                    report, case_name, completed.returncode, authored_hash
                )
                run_record.update(checked)
                run_record["status"] = "passed"
            except subprocess.TimeoutExpired as error:
                (run_dir / "stdout.txt").write_text(_decode_capture(error.stdout), encoding="utf-8")
                (run_dir / "stderr.txt").write_text(_decode_capture(error.stderr), encoding="utf-8")
                run_record["status"] = "failed"
                run_record["error"] = f"engine run timed out after {timeout} seconds"
                raise SmokeError(f"{case_name}: {run_record['error']}") from error
            except (OSError, SmokeError) as error:
                run_record["status"] = "failed"
                run_record["error"] = str(error)
                raise SmokeError(f"{case_name}: {error}") from error
            finally:
                shutil.rmtree(workspace, ignore_errors=True)
                _write_json(output / "smoke.json", summary)
    except SmokeError:
        summary["status"] = "failed"
        _write_json(output / "smoke.json", summary)
        raise

    summary["status"] = "passed"
    summary["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    _write_json(output / "smoke.json", summary)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path, help="Bifrost executable to exercise")
    parser.add_argument("--output", required=True, type=Path, help="empty directory for smoke evidence")
    parser.add_argument(
        "--timeout", type=int, default=120,
        help=f"per-process timeout in seconds (1-{MAX_TIMEOUT_SECONDS}, default: 120)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = run_smoke(args.binary, args.output, args.timeout)
    except SmokeError as error:
        print(f"smoke failed: {error}", file=sys.stderr)
        return 1
    print(
        f"focused smoke passed for Bifrost {result['engine_version']}: "
        "dynamic-evaluation positive=1, near-miss=0; full copied content remains unqualified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
