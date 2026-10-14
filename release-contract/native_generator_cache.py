#!/usr/bin/env python3
"""Identify and verify cached producer builds without qualifying generated packs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys

import native_generation as generation


RECIPE_PATHS = (
    ".github/workflows/native-packs.yml",
    "release-contract/native_generator_cache.py",
    "release-contract/native_generation.py",
)
MANIFEST_FIELDS = {
    "schema_version", "identity", "identity_sha256", "binary_sha256",
    "build_receipt_sha256", "origin",
}
ORIGIN_FIELDS = {
    "repository", "source_commit", "workflow_ref", "workflow_sha", "run_id", "run_attempt",
}
BUILD_ENVIRONMENT = {
    "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTDOC",
    "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "CC", "CXX", "AR",
    "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "HOST_CC", "HOST_CXX",
    "HOST_AR", "HOST_CFLAGS", "HOST_CXXFLAGS", "TARGET_CC", "TARGET_CXX",
    "TARGET_AR", "TARGET_CFLAGS", "TARGET_CXXFLAGS", "SDKROOT",
}


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _regular_file(path: Path) -> bytes:
    if not stat.S_ISREG(path.lstat().st_mode):
        generation._fail(f"cache evidence must be a regular file without a symlink: {path}")
    return path.read_bytes()


def _required(environment, name):
    value = environment.get(name)
    if not isinstance(value, str) or not value.strip():
        generation._fail(f"producer cache requires {name}")
    return value


def _cargo_configs(environment):
    """Bind global and ancestor Cargo configuration outside the pinned source."""
    cargo_home = Path(environment.get("CARGO_HOME", str(Path.home() / ".cargo")))
    build_parent = Path(_required(environment, "RUNNER_TEMP")).resolve()
    locations = [cargo_home, *(parent / ".cargo" for parent in (build_parent, *build_parent.parents))]
    return [
        {name: generation._sha256_bytes(_regular_file(directory / name))
         if (directory / name).exists() or (directory / name).is_symlink() else None
         for name in ("config", "config.toml")}
        for directory in locations
    ]


def build_identity(root: Path, config: Path, environment) -> dict:
    generator, _, _, _ = generation._validate_config(root.resolve(), config)
    if "build" not in generator:
        generation._fail("producer cache requires a source-built generator")
    toolchain = generator["build"]["rust_toolchain"]
    rustc = subprocess.check_output(["rustc", f"+{toolchain}", "-vV"], env=environment, text=True).strip()
    cargo = subprocess.check_output(["cargo", f"+{toolchain}", "-V"], env=environment, text=True).strip()
    hosts = [line.removeprefix("host: ") for line in rustc.splitlines() if line.startswith("host: ")]
    releases = [line.removeprefix("release: ") for line in rustc.splitlines() if line.startswith("release: ")]
    if len(hosts) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]+", hosts[0]) or releases != [toolchain]:
        generation._fail("actual rustc host/release differs from the pinned toolchain")
    if not cargo.startswith("cargo "):
        generation._fail("cannot identify the actual Cargo toolchain")
    return {
        "schema_version": 1,
        "generator": generator,
        "toolchain": {"rustc": rustc, "cargo": cargo},
        "platform": {
            "runner_os": _required(environment, "RUNNER_OS"),
            "runner_arch": _required(environment, "RUNNER_ARCH"),
            "image_os": _required(environment, "ImageOS"),
            "image_version": _required(environment, "ImageVersion"),
            "system": platform.system(), "machine": platform.machine(),
        },
        "build": {
            "target": hosts[0], "package": "brokk-bifrost-semantic-packs",
            "binary": "bifrost-semantic-pack", "default_features": True,
            "features": ["release-tooling"], "profile": "release", "locked": True,
        },
        "environment": {
            key: value for key, value in environment.items()
            if key in BUILD_ENVIRONMENT or key.startswith(("CARGO_BUILD_", "CARGO_PROFILE_", "CARGO_TARGET_"))
        },
        "cargo_configs": _cargo_configs(environment),
        "recipe": {path: generation._sha256_bytes(_regular_file(root / path)) for path in RECIPE_PATHS},
    }


def cache_key(identity: dict) -> str:
    return "native-generator-v2-" + generation._sha256_bytes(_canonical(identity))


def _expected(root: Path, config: Path, expected_path: Path, environment):
    expected = generation._load_json(_regular_file(expected_path), str(expected_path))
    current = build_identity(root, config, environment)
    if _canonical(expected) != _canonical(current):
        generation._fail("producer build inputs changed after cache identity was computed")
    return current


def _payload(identity: dict, cache: Path):
    if not stat.S_ISDIR(cache.lstat().st_mode):
        generation._fail("producer cache must be a real directory without a symlink")
    binary = cache / "bifrost-semantic-pack"
    binary_sha = generation._sha256_bytes(_regular_file(binary))
    if not os.access(binary, os.X_OK):
        generation._fail("cached producer must be executable")
    if identity["generator"]["binary_sha256"] not in (None, binary_sha):
        generation._fail("cached producer differs from the configured binary pin")
    receipt_bytes = _regular_file(cache / "build.json")
    receipt = generation._load_json(receipt_bytes, "cached build receipt")
    generation._validate_build_attestation(identity["generator"], receipt, binary_sha)
    return binary_sha, generation._sha256_bytes(receipt_bytes)


def _validate_origin(origin, repository):
    if not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS:
        generation._fail("cache origin must contain the exact build provenance fields")
    if any(not isinstance(value, str) or not value.strip() for value in origin.values()):
        generation._fail("cache origin provenance must be nonempty strings")
    if (origin["repository"] != repository
            or not origin["workflow_ref"].startswith(f"{repository}/.github/workflows/native-packs.yml@")
            or not origin["workflow_ref"].split("@", 1)[1]
            or any(not generation.COMMIT_RE.fullmatch(origin[key]) for key in ("source_commit", "workflow_sha"))
            or any(not re.fullmatch(r"[1-9][0-9]*", origin[key]) for key in ("run_id", "run_attempt"))):
        generation._fail("cache origin provenance is invalid")


def record(root: Path, config: Path, cache: Path, expected_path: Path, environment) -> dict:
    identity = _expected(root, config, expected_path, environment)
    if {path.name for path in cache.iterdir()} != {"bifrost-semantic-pack", "build.json"}:
        generation._fail("fresh producer cache must contain only a completed binary and build receipt")
    binary_sha, receipt_sha = _payload(identity, cache)
    origin = {
        "repository": _required(environment, "GITHUB_REPOSITORY"),
        "source_commit": generation._source_provenance(root)["commit"],
        "workflow_ref": _required(environment, "GITHUB_WORKFLOW_REF"),
        "workflow_sha": _required(environment, "GITHUB_WORKFLOW_SHA"),
        "run_id": _required(environment, "GITHUB_RUN_ID"),
        "run_attempt": _required(environment, "GITHUB_RUN_ATTEMPT"),
    }
    _validate_origin(origin, environment["GITHUB_REPOSITORY"])
    manifest = {
        "schema_version": 1, "identity": identity,
        "identity_sha256": generation._sha256_bytes(_canonical(identity)),
        "binary_sha256": binary_sha, "build_receipt_sha256": receipt_sha, "origin": origin,
    }
    with (cache / "cache.json").open("x") as stream:
        stream.write(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    return manifest


def verify(root: Path, config: Path, cache: Path, expected_path: Path, environment) -> dict:
    identity = _expected(root, config, expected_path, environment)
    binary_sha, receipt_sha = _payload(identity, cache)
    if {path.name for path in cache.iterdir()} != {"bifrost-semantic-pack", "build.json", "cache.json"}:
        generation._fail("producer cache contains incomplete or unexpected evidence")
    manifest = generation._load_json(_regular_file(cache / "cache.json"), "producer cache manifest")
    if (not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS
            or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1):
        generation._fail("unsupported or malformed producer cache manifest")
    if (_canonical(manifest["identity"]) != _canonical(identity)
            or manifest["identity_sha256"] != generation._sha256_bytes(_canonical(identity))):
        generation._fail("producer cache identity mismatch")
    if manifest["binary_sha256"] != binary_sha or manifest["build_receipt_sha256"] != receipt_sha:
        generation._fail("producer cache payload digest mismatch")
    _validate_origin(manifest["origin"], _required(environment, "GITHUB_REPOSITORY"))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("identity", "record", "verify"))
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--identity", required=True, type=Path, help="expected identity outside the cache")
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    config = root / args.config
    try:
        if args.command == "identity":
            identity = build_identity(root, config, os.environ)
            args.identity.write_bytes(_canonical(identity) + b"\n")
            print(f"key={cache_key(identity)}")
            print(f"target={identity['build']['target']}")
        else:
            if args.cache is None:
                parser.error("record and verify require --cache")
            operation = record if args.command == "record" else verify
            manifest = operation(root, config, args.cache, args.identity, os.environ)
            print(json.dumps({"key": cache_key(manifest["identity"]), "origin": manifest["origin"]}, sort_keys=True))
    except (generation.NativeGenerationError, OSError, subprocess.CalledProcessError) as error:
        print(f"producer-cache-error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
