#!/usr/bin/env python3
"""Audit a downloaded pack descriptor and its adjacent artifacts offline.

This verifies release integrity and descriptor-to-archive correspondence. It
does not claim consumer behavior or completeness beyond what the descriptor
records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tarfile
import zlib
import tempfile
from pathlib import Path
from typing import Any

import content

CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "release-contract"
sys.path.insert(0, str(CONTRACT_ROOT))
import native_release
import release


class AuditError(Exception):
    """The descriptor, artifact, or derived content inventory disagrees."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _content_map(items: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    result: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["kind"], item["identity"], item["path"])
        if key in result:
            raise AuditError(f"duplicate derived content identity: {key}")
        result[key] = item
    return result


def _compare_contents(expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> None:
    expected_map = _content_map(expected)
    actual_map = _content_map(actual)
    if expected_map.keys() != actual_map.keys():
        missing = sorted(set(expected_map) - set(actual_map))
        extra = sorted(set(actual_map) - set(expected_map))
        raise AuditError(f"descriptor content inventory differs (missing={missing}, extra={extra})")
    for key in sorted(expected_map):
        if _canonical(expected_map[key]) != _canonical(actual_map[key]):
            raise AuditError(f"descriptor content row differs from archive: {key}")


def _verify_sidecar(artifact: dict[str, Any], path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise AuditError(f"artifact sidecar is missing or not a regular file: {path.name}.sha256")
    raw = path.read_text(encoding="utf-8")
    match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)\n?", raw)
    if not match or match.group(1) != artifact["sha256"] or match.group(2) != artifact["name"]:
        raise AuditError(f"artifact sidecar differs from descriptor: {path.name}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _audit_rules(archive: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = native_release.archive_files(archive)
    with tempfile.TemporaryDirectory(prefix="bifrost-pack-audit-rules-") as temporary:
        root = Path(temporary)
        for name, data in files.items():
            target = root / release.safe_path(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        lock = content.verify_content(root)
        # A release's source tuple records the pack source revision. The content
        # lock independently records the origin revision; retain and compare both.
        if manifest["source"]["repository"] != manifest["pack"]["repository"]:
            raise AuditError("rules source repository differs from pack repository")
        derived = release.public_contents(root, lock, "rules")
        referenced_manifests = {
            item["path"] for item in lock["files"]
            if item["path"].startswith("rules/") and item["path"].endswith("/manifest.json")
        }
        referenced_policies: set[str] = set()
        for manifest_path in referenced_manifests:
            native_manifest, _ = release.load_json(root / manifest_path)
            parent = manifest_path.rsplit("/", 1)[0]
            for policy in native_manifest["policies"]:
                referenced_policies.add(parent + "/" + release.safe_path(policy["path"]))
        archived_policy_paths = {
            entry["path"] for entry in lock["files"]
            if entry["path"].startswith("rules/") and "/policies/" in entry["path"]
            and entry["path"].endswith(".rqlp")
        }
        if archived_policy_paths != referenced_policies:
            raise AuditError("public rule archive has missing or unindexed policy documents")
        allowed = {entry["path"] for entry in lock["files"]}
        allowed.update({"LICENSE", "NOTICE.md", "README.md", "content-lock.json"})
        allowed.update({
            "scripts/content.py",
            "scripts/smoke.py",
            "tests/cases/dynamic-evaluation/positive.py",
            "tests/cases/dynamic-evaluation/near-miss.py",
        })
        # Current source releases carry reproduction tooling, documentation,
        # tests and research as metadata. Use the source builder's same bounded
        # inventory; these paths never become policy/content rows.
        allowed.update(name for name, _ in content._bundle_inputs(root, lock))
        extras = sorted(set(files) - allowed)
        if extras:
            raise AuditError(f"rules source archive has unapproved or unindexed files: {extras}")
        lock_record = {
            "aggregate_sha256": lock["aggregate_sha256"],
            "source_repository": lock["source"]["repository"],
            "source_revision": lock["source"]["revision"],
            "classification_counts": {},
            "license_counts": {},
            "locked_file_count": len(lock["files"]),
        }
        for entry in lock["files"]:
            classification = entry["classification"]
            license_name = entry["license"]
            lock_record["classification_counts"][classification] = lock_record["classification_counts"].get(classification, 0) + 1
            lock_record["license_counts"][license_name] = lock_record["license_counts"].get(license_name, 0) + 1
        origin = manifest.get("content_origin")
        if origin:
            if (origin.get("repository"), origin.get("commit")) != (lock["source"]["repository"], lock["source"]["revision"]):
                raise AuditError("descriptor content origin differs from archived content lock")
            # This field identifies the original full source lock. Component
            # archives contain a filtered lock with a different digest.
            lock_record["declared_source_lock_sha256"] = origin.get("lock_sha256")
            lock_record["archive_lock_sha256"] = release.digest(files["content-lock.json"])
        return derived, lock_record


def _audit_native(archive: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = native_release.archive_files(archive)
    index = json.loads(files["bifrost-semantic-packs/index.json"])
    generator_version = index.get("generator", {}).get("version")
    if not isinstance(generator_version, str) or not generator_version:
        raise AuditError("native release index has no generator version")
    derived = native_release.native_contents(archive, generator_version=generator_version)
    completeness: dict[str, int] = {}
    for item in derived:
        state = item.get("completeness", "unspecified")
        completeness[state] = completeness.get(state, 0) + 1
    return derived, {
        "generator_version": generator_version,
        "index_schema_version": index.get("schema_version"),
        "model_count": len(derived),
        "completeness_counts": completeness,
    }


def _selection(manifest_path: Path, manifest: dict[str, Any], profile_path: Path, allow_unqualified: bool, dependency_paths: list[Path]) -> dict[str, Any]:
    profile, profile_bytes = release.load_json(profile_path)
    profile_record = {"sha256": hashlib.sha256(profile_bytes).hexdigest(), "profile": profile}
    candidates = [manifest_path]
    dependencies = []
    for dependency_path in dependency_paths:
        dependency_path = Path(dependency_path).expanduser()
        if dependency_path.is_symlink() or not dependency_path.is_file():
            raise AuditError(f"dependency manifest must be a regular file: {dependency_path}")
        dependency_path = dependency_path.resolve(strict=True)
        dependency, _ = release.load_json(dependency_path)
        release.validate_manifest(dependency)
        for artifact in dependency["artifacts"]:
            artifact_path = dependency_path.parent / release.safe_path(artifact["name"])
            release.verify_artifact(artifact, artifact_path)
            _verify_sidecar(artifact, Path(str(artifact_path) + ".sha256"))
        candidates.append(dependency_path)
        dependencies.append({"pack": dependency["pack"], "release_version": dependency["release_version"], "source": dependency["source"]})
    channel = "prerelease" if release.semver(manifest["release_version"])[3] == 0 else "stable"
    try:
        receipt = release.select_release(
            candidates,
            profile,
            manifest["pack"]["id"],
            channel=channel,
            version=manifest["release_version"],
            commit=manifest["source"]["commit"],
            allow_unqualified=allow_unqualified,
        )
    except release.ReleaseError as error:
        return {"status": "rejected", "error": error.code, "message": str(error), "diagnostic": True, "allow_unqualified": allow_unqualified, "engine_profile": profile_record, "dependencies_supplied": dependencies}
    return {"status": "selected", "diagnostic": True, "allow_unqualified": allow_unqualified, "engine_profile": profile_record, "receipt": receipt}


def audit_tuple(manifest_path: Path, profile_path: Path | None = None, allow_unqualified: bool = False, dependency_paths: list[Path] | None = None, _visited: frozenset[Path] = frozenset()) -> dict[str, Any]:
    manifest_path = Path(manifest_path).expanduser()
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise AuditError("manifest must be a regular file")
    manifest_path = manifest_path.resolve(strict=True)
    if manifest_path in _visited:
        raise AuditError(f"cyclic dependency descriptor: {manifest_path}")
    manifest, manifest_bytes = release.load_json(manifest_path)
    release.validate_manifest(manifest)
    if manifest["pack"]["visibility"] != "public":
        raise AuditError("audit accepts public release descriptors only")
    if allow_unqualified and profile_path is None:
        raise AuditError("--allow-unqualified requires --engine-profile")

    roles = {artifact["role"] for artifact in manifest["artifacts"]}
    if manifest["pack"]["id"] == "bifrost.public.rules" and roles == {"source"}:
        kind = "rules"
    elif manifest["pack"]["id"] == "bifrost.public.packs" and "native" in roles and roles <= {"native", "source"}:
        kind = "native"
    else:
        raise AuditError("audit supports public rules source and public native pack releases only")

    artifacts: list[dict[str, Any]] = []
    primary_archives: list[Path] = []
    for artifact in manifest["artifacts"]:
        path = manifest_path.parent / release.safe_path(artifact["name"])
        if path.parent.resolve() != manifest_path.parent.resolve():
            raise AuditError("artifact must be adjacent to the release manifest")
        release.verify_artifact(artifact, path)
        sidecar_hash = _verify_sidecar(artifact, Path(str(path) + ".sha256"))
        artifacts.append({**artifact, "sidecar_sha256": sidecar_hash})
        if artifact["format"] == "tar.gz" and artifact["role"] in ({"source"} if kind == "rules" else {"native"}):
            primary_archives.append(path)

    if len(primary_archives) != 1:
        raise AuditError("expected exactly one primary source/native tar.gz archive")
    primary_archive = primary_archives[0]
    derived, detail = _audit_rules(primary_archive, manifest) if kind == "rules" else _audit_native(primary_archive)
    _compare_contents(manifest["contents"], derived)

    policies = [row for row in derived if row["kind"] == "policy"]
    models = [row for row in derived if row["kind"] == "semantic-model"]
    result: dict[str, Any] = {
        "audit_schema_version": 1,
        "status": "integrity_verified",
        "scope": "offline descriptor, sidecar, archive, and content-row integrity audit; no engine behavior qualification",
        "pack": manifest["pack"],
        "release_version": manifest["release_version"],
        "source": manifest["source"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "archive_sha256": release.digest(primary_archive.read_bytes()),
        "content_kind": kind,
        "descriptor_content_count": len(derived),
        "policy_count": len(policies),
        "semantic_model_count": len(models),
        "policy_identities": [
            {"id": row["identity"], "path": row["path"], "sha256": row["sha256"], "authored_hash": row.get("authored_hash"), "resolved_semantic_hash": row.get("resolved_semantic_hash")}
            for row in policies
        ],
        "semantic_model_identities": [
            {"id": row["identity"], "version": row.get("content_version"), "path": row["path"], "sha256": row["sha256"], "completeness": row.get("completeness")}
            for row in models
        ],
        "artifacts": artifacts,
        "integrity": {"status": "verified", "evidence": ["all descriptor-indexed artifact sizes and SHA-256 values verified", "adjacent SHA-256 sidecars match artifact descriptors", "archive content was independently decoded and its derived descriptor rows match exactly"]},
        "behavior": {"status": "pending", "evidence": ["this audit did not execute or qualify the content with a consumer engine"]},
        "descriptor_qualification": manifest["qualification"],
        "details": detail,
    }
    if kind == "rules":
        result["public_content_lock"] = detail
    if profile_path is not None:
        result["selection"] = _selection(manifest_path, manifest, profile_path, allow_unqualified, dependency_paths or [])
    if dependency_paths:
        audited_dependencies = []
        for dependency_path in dependency_paths:
            audited_dependencies.append(audit_tuple(dependency_path, _visited=_visited | {manifest_path}))
        result["audited_dependencies"] = audited_dependencies
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="downloaded pack-release.json")
    parser.add_argument("--output", required=True, type=Path, help="write audit JSON here")
    parser.add_argument("--engine-profile", type=Path, help="optional actual pack-engine-profile JSON")
    parser.add_argument("--allow-unqualified", action="store_true", help="diagnostic selector option; never changes integrity checks")
    parser.add_argument("--dependency-manifest", type=Path, action="append", default=[], help="exact dependency descriptor with its adjacent artifacts; repeat as needed")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = audit_tuple(args.manifest, args.engine_profile, args.allow_unqualified, args.dependency_manifest)
        output = args.output.expanduser()
        protected = {Path(args.manifest).expanduser().resolve()}
        if args.engine_profile:
            protected.add(args.engine_profile.expanduser().resolve())
        protected.update(path.expanduser().resolve() for path in args.dependency_manifest)
        for input_manifest in [Path(args.manifest).expanduser().resolve(), *(path.expanduser().resolve() for path in args.dependency_manifest)]:
            candidate, _ = release.load_json(input_manifest)
            for artifact in candidate["artifacts"]:
                artifact_path = input_manifest.parent / artifact["name"]
                protected.add(artifact_path.resolve())
                protected.add(Path(str(artifact_path) + ".sha256").resolve())
        if output.is_symlink() or output.resolve() in protected:
            raise AuditError("output must not overwrite a manifest, profile, dependency, or release artifact")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=output.name + ".", suffix=".tmp", dir=output.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            os.replace(temporary, output)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        print(json.dumps({"status": result["status"], "pack": result["pack"], "release_version": result["release_version"], "output": str(output)}))
        return 0
    except (AuditError, release.ReleaseError, content.ContentError, tarfile.TarError, zlib.error, OSError, ValueError, KeyError, TypeError) as error:
        code = error.code if isinstance(error, release.ReleaseError) else "integrity-error"
        print(json.dumps({"error": code, "message": str(error)}), file=sys.stderr)
        return release.ERROR_EXIT.get(code, 7)


if __name__ == "__main__":
    raise SystemExit(main())
