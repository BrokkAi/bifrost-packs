#!/usr/bin/env python3
"""Generate a deterministic inventory of runnable RQL policy documents."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import quote


README_START = "<!-- rule-stats:start -->"
README_END = "<!-- rule-stats:end -->"
SUPPORTED_POLICY_SCHEMA = 1
SUPPORTED_RQL_SCHEMA = 1


class InventoryError(Exception):
    """Raised when the repository cannot be inventoried reliably."""


@dataclass(frozen=True)
class Atom:
    value: str
    quoted: bool = False


# `Any` keeps this recursive alias usable with the repository's Python 3.9 floor.
Node = Any


class Vector(list):
    """Bracketed literal vector; its elements are not syntax forms."""


@dataclass(frozen=True)
class Rule:
    path: str
    name: str
    rule_id: str
    severity: str | None
    pack_id: str | None
    category: str | None
    supported_languages: tuple[str, ...] | None
    activation: str | None
    query_languages: tuple[str, ...]
    tags: tuple[str, ...]


def _tokenize(source: str) -> list[Atom | str]:
    tokens: list[Atom | str] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char == ";":
            newline = source.find("\n", index)
            index = len(source) if newline < 0 else newline + 1
            continue
        if char in "()[]":
            tokens.append(char)
            index += 1
            continue
        if char == '"':
            index += 1
            value: list[str] = []
            while index < len(source):
                char = source[index]
                if char == '"':
                    index += 1
                    break
                if char == "\\":
                    index += 1
                    if index >= len(source):
                        raise InventoryError("unterminated escape in quoted string")
                    escaped = source[index]
                    value.append(
                        {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}.get(
                            escaped, escaped
                        )
                    )
                    index += 1
                    continue
                value.append(char)
                index += 1
            else:
                raise InventoryError("unterminated quoted string")
            tokens.append(Atom("".join(value), quoted=True))
            continue

        start = index
        while index < len(source) and not source[index].isspace() and source[index] not in '()[];"':
            index += 1
        if start == index:
            raise InventoryError(f"unexpected character {source[index]!r}")
        tokens.append(Atom(source[start:index]))
    return tokens


def parse_sexpr(source: str) -> Node:
    """Parse one policy S-expression, including bracketed vectors."""

    tokens = _tokenize(source)
    if not tokens:
        raise InventoryError("empty policy document")
    cursor = 0

    def parse_node() -> Node:
        nonlocal cursor
        if cursor >= len(tokens):
            raise InventoryError("unexpected end of policy document")
        token = tokens[cursor]
        cursor += 1
        if isinstance(token, Atom):
            return token
        if token not in ("(", "["):
            raise InventoryError(f"unexpected closing delimiter {token!r}")
        closing = ")" if token == "(" else "]"
        items: list[Node] = []
        while cursor < len(tokens) and tokens[cursor] != closing:
            if tokens[cursor] in (")", "]"):
                raise InventoryError("mismatched closing delimiter")
            items.append(parse_node())
        if cursor >= len(tokens):
            raise InventoryError(f"missing closing delimiter {closing!r}")
        cursor += 1
        return items if token == "(" else Vector(items)

    expression = parse_node()
    if cursor != len(tokens):
        raise InventoryError("multiple top-level expressions")
    return expression


def _scalar(node: Node | None) -> str | None:
    return node.value if isinstance(node, Atom) else None


def _operator(node: Node | None, value: str) -> bool:
    return isinstance(node, Atom) and not node.quoted and node.value == value


def _top_level_fields(root: list[Node]) -> dict[str, Node]:
    fields: dict[str, Node] = {}
    index = 1
    while index < len(root):
        node = root[index]
        if isinstance(node, Atom) and not node.quoted and node.value.startswith(":"):
            if index + 1 >= len(root):
                raise InventoryError(f"top-level field {node.value} has no value")
            if node.value in fields:
                raise InventoryError(f"duplicate top-level field {node.value}")
            fields[node.value] = root[index + 1]
            index += 2
        elif isinstance(node, list):
            index += 1
        else:
            raise InventoryError(f"unexpected top-level policy token {_scalar(node)!r}")
    return fields


def _nested_forms(node: Node) -> Iterable[list[Node]]:
    if not isinstance(node, list):
        return
    if not isinstance(node, Vector):
        yield node
    for child in node:
        yield from _nested_forms(child)


def _language_scopes(root: Node) -> tuple[str, ...]:
    languages: set[str] = set()
    for form in _nested_forms(root):
        if len(form) >= 2 and _operator(form[0], "language"):
            value = _scalar(form[1])
            if value:
                languages.add(value)
    return tuple(sorted(languages))


def _tag_values(node: Node | None) -> tuple[str, ...]:
    if isinstance(node, list):
        return tuple(sorted({value for item in node if (value := _scalar(item))}))
    value = _scalar(node)
    return (value,) if value else ()


def _validate_policy(path: Path, relative_path: str) -> tuple[str, str, str | None, tuple[str, ...], tuple[str, ...]]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise InventoryError(f"cannot read {relative_path}: {error}") from error
    try:
        root = parse_sexpr(source)
    except InventoryError as error:
        raise InventoryError(f"{relative_path}: {error}") from error
    if not isinstance(root, list) or isinstance(root, Vector) or not root or not _operator(root[0], "policy"):
        raise InventoryError(f"{relative_path}: document root must be (policy ...)")

    fields = _top_level_fields(root)
    schema = _scalar(fields.get(":schema-version"))
    if schema is None:
        raise InventoryError(f"{relative_path}: missing top-level :schema-version")
    if schema != str(SUPPORTED_POLICY_SCHEMA):
        raise InventoryError(f"{relative_path}: unsupported policy schema {schema!r}")

    rule_id = _scalar(fields.get(":id"))
    name = _scalar(fields.get(":name"))
    if not rule_id:
        raise InventoryError(f"{relative_path}: missing top-level :id")
    if not name:
        raise InventoryError(f"{relative_path}: missing top-level :name")
    severity = _scalar(fields.get(":severity"))

    rql_count = 0
    for form in _nested_forms(root):
        if form and _operator(form[0], "rql"):
            rql_count += 1
            rql_fields: dict[str, Node] = {}
            index = 1
            while index < len(form):
                node = form[index]
                if isinstance(node, Atom) and not node.quoted and node.value.startswith(":"):
                    if index + 1 >= len(form):
                        raise InventoryError(f"{relative_path}: RQL field {node.value} has no value")
                    if node.value in rql_fields:
                        raise InventoryError(f"{relative_path}: duplicate RQL field {node.value}")
                    rql_fields[node.value] = form[index + 1]
                    index += 2
                else:
                    index += 1
            version = _scalar(rql_fields.get(":schema-version"))
            if version is None:
                raise InventoryError(f"{relative_path}: RQL form missing :schema-version")
            if version != str(SUPPORTED_RQL_SCHEMA):
                raise InventoryError(f"{relative_path}: unsupported RQL schema {version!r}")
    if not rql_count:
        raise InventoryError(f"{relative_path}: missing RQL form with explicit :schema-version")

    tags = _tag_values(fields.get(":tags"))
    return rule_id, name, severity, _language_scopes(root), tags


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _resolve_inside(root: Path, path: Path, description: str, must_exist: bool = True) -> Path:
    try:
        resolved = path.resolve(strict=must_exist)
    except OSError as error:
        raise InventoryError(f"cannot resolve {description}: {error}") from error
    if not _inside(resolved, root.resolve()):
        raise InventoryError(f"{description} resolves outside the repository")
    return resolved


def _load_json(path: Path, description: str) -> Any:
    def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise InventoryError(f"{description}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    except InventoryError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InventoryError(f"cannot read {description}: {error}") from error


def _safe_manifest_policy_path(root: Path, manifest: Path, value: Any) -> tuple[Path, str]:
    if not isinstance(value, str) or not value:
        raise InventoryError(f"{manifest.relative_to(root)}: policy path must be a nonempty string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "\\" in value:
        raise InventoryError(f"{manifest.relative_to(root)}: unsafe policy path {value!r}")
    rules_root = _resolve_inside(root, root / "rules", "rules directory")
    candidate = _resolve_inside(root, manifest.parent / Path(*pure.parts), f"manifest policy path {value!r}")
    if not _inside(candidate, rules_root) or candidate.suffix != ".rqlp" or not candidate.is_file():
        raise InventoryError(f"{manifest.relative_to(root)}: policy path {value!r} is not a rules/*.rqlp file")
    return candidate, candidate.relative_to(root.resolve()).as_posix()


def _load_manifests(root: Path, discovered: dict[str, Path]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    manifests = sorted((root / "rules").glob("*/manifest.json"))
    if not manifests:
        return {}, {}

    policy_metadata: dict[str, dict[str, Any]] = {}
    pack_metadata: dict[str, dict[str, str]] = {}
    pack_ids: set[str] = set()
    for manifest in manifests:
        _resolve_inside(root, manifest, f"manifest {manifest}")
        data = _load_json(manifest, manifest.relative_to(root).as_posix())
        if not isinstance(data, dict):
            raise InventoryError(f"{manifest.relative_to(root)}: manifest must be a JSON object")
        pack_id = data.get("id")
        if not isinstance(pack_id, str) or not pack_id:
            raise InventoryError(f"{manifest.relative_to(root)}: missing manifest id")
        if pack_id in pack_ids:
            raise InventoryError(f"duplicate manifest id {pack_id!r}")
        pack_ids.add(pack_id)
        pack_metadata[pack_id] = {
            "name": data.get("name") if isinstance(data.get("name"), str) else pack_id,
            "path": manifest.parent.relative_to(root).as_posix(),
        }
        entries = data.get("policies")
        if not isinstance(entries, list):
            raise InventoryError(f"{manifest.relative_to(root)}: policies must be a JSON array")
        pack_root = _resolve_inside(root, manifest.parent, f"manifest directory {manifest.parent}")
        seen_paths: set[str] = set()
        for entry_index, entry in enumerate(entries):
            label = f"{manifest.relative_to(root)} policies[{entry_index}]"
            if not isinstance(entry, dict):
                raise InventoryError(f"{label} must be an object")
            policy_path, relative = _safe_manifest_policy_path(root, manifest, entry.get("path"))
            if not _inside(policy_path, pack_root):
                raise InventoryError(f"{label} policy path escapes its pack directory")
            if relative in seen_paths or relative in policy_metadata:
                raise InventoryError(f"duplicate manifest policy path {relative!r}")
            seen_paths.add(relative)
            rule_id = entry.get("id")
            if not isinstance(rule_id, str) or not rule_id:
                raise InventoryError(f"{label} missing policy id")
            supported = entry.get("supported_languages")
            if supported is not None:
                if not isinstance(supported, list) or any(not isinstance(lang, str) or not lang for lang in supported):
                    raise InventoryError(f"{label} supported_languages must be an array of nonempty strings")
                if len(set(supported)) != len(supported):
                    raise InventoryError(f"{label} supported_languages contains duplicates")
                supported = tuple(sorted(supported))
            category = entry.get("category")
            if category is not None and (not isinstance(category, str) or not category):
                raise InventoryError(f"{label} category must be a nonempty string when present")
            activation = entry.get("activation")
            if activation is not None and (not isinstance(activation, str) or not activation):
                raise InventoryError(f"{label} activation must be a nonempty string when present")
            policy_metadata[relative] = {
                "id": rule_id,
                "pack_id": pack_id,
                "category": category,
                "supported_languages": supported,
                "activation": activation,
            }
            if relative not in discovered:
                raise InventoryError(f"{label} references a policy missing from inventory: {relative}")

    unlisted = sorted(set(discovered) - set(policy_metadata))
    if unlisted:
        raise InventoryError(f"policies missing manifest records: {', '.join(unlisted)}")
    return policy_metadata, pack_metadata


def _case_policy_path(root: Path, value: str) -> tuple[Path | None, str | None]:
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or "\\" in value:
        return None, None
    candidate = (root / Path(*pure.parts)).resolve(strict=False)
    root_resolved = root.resolve()
    if not _inside(candidate, root_resolved):
        return None, None
    rules_root = (root / "rules").resolve(strict=False)
    if not _inside(candidate, rules_root):
        return None, None
    return candidate, candidate.relative_to(root_resolved).as_posix()


def _validate_case_fixtures(root: Path, case_file: Path, case: dict[str, Any], index: int) -> None:
    values: list[Any] = []
    if "fixture" in case:
        values.append(case["fixture"])
    if "fixtures" in case:
        fixture_list = case["fixtures"]
        if not isinstance(fixture_list, list):
            raise InventoryError(f"{case_file.relative_to(root)} cases[{index}].fixtures must be an array")
        values.extend(fixture_list)
    for value in values:
        if not isinstance(value, str) or not value:
            raise InventoryError(f"{case_file.relative_to(root)} cases[{index}] has an invalid fixture path")
        pure = PurePosixPath(value)
        if pure.is_absolute() or ".." in pure.parts or "\\" in value:
            raise InventoryError(f"{case_file.relative_to(root)} cases[{index}] has an unsafe fixture path")
        fixture = _resolve_inside(root, root / Path(*pure.parts), f"fixture {value!r}")
        if not fixture.exists():
            raise InventoryError(f"{case_file.relative_to(root)} cases[{index}] fixture is missing: {value}")


def _load_case_counts(root: Path, rule_by_path: dict[str, Rule]) -> dict[str, dict[str, int]]:
    cases_root = root / "tests" / "cases"
    if not cases_root.exists():
        return {}
    _resolve_inside(root, cases_root, "tests/cases directory")
    counts: dict[str, Counter[str]] = {}
    for case_file in sorted(cases_root.rglob("*.json")):
        _resolve_inside(root, case_file, f"case record {case_file}")
        record = _load_json(case_file, case_file.relative_to(root).as_posix())
        if not isinstance(record, dict):
            continue
        path_value = record.get("policy_path", record.get("policy"))
        rule_id = record.get("policy_id")
        cases = record.get("cases")
        # JSON files without an explicit policy association are runner inputs, not
        # per-policy expected-finding records for this catalog.
        if path_value is None or rule_id is None or cases is None:
            continue
        if not isinstance(path_value, str) or not isinstance(rule_id, str) or not isinstance(cases, list):
            raise InventoryError(f"{case_file.relative_to(root)}: malformed policy case record")
        resolved, relative = _case_policy_path(root, path_value)
        if resolved is None or relative is None:
            continue
        if not _inside(resolved, (root / "rules").resolve(strict=False)):
            continue
        if not resolved.is_file() or relative not in rule_by_path:
            raise InventoryError(f"{case_file.relative_to(root)}: policy path does not select an inventoried rule")
        if rule_by_path[relative].rule_id != rule_id:
            raise InventoryError(f"{case_file.relative_to(root)}: policy_id does not match {relative}")
        counter = counts.setdefault(relative, Counter())
        for case_index, case in enumerate(cases):
            if not isinstance(case, dict) or "expected_findings" not in case:
                raise InventoryError(
                    f"{case_file.relative_to(root)} cases[{case_index}] must declare expected_findings"
                )
            expected = case["expected_findings"]
            if not isinstance(expected, list):
                raise InventoryError(
                    f"{case_file.relative_to(root)} cases[{case_index}].expected_findings must be an array"
                )
            _validate_case_fixtures(root, case_file, case, case_index)
            counter["positive" if expected else "zero_expected"] += 1
    return {path: dict(counter) for path, counter in counts.items()}


def build_inventory(repo: Path) -> dict[str, Any]:
    root = repo.resolve()
    rules_root = root / "rules"
    if not rules_root.is_dir():
        raise InventoryError(f"repository has no rules/ directory: {root}")
    rules_root = _resolve_inside(root, rules_root, "rules directory")

    discovered: dict[str, Path] = {}
    for path in sorted(rules_root.rglob("*.rqlp")):
        resolved = _resolve_inside(root, path, f"policy {path}")
        if not resolved.is_file():
            continue
        relative = resolved.relative_to(root).as_posix()
        discovered[relative] = resolved

    metadata_by_path, packs = _load_manifests(root, discovered)
    manifest_mode = bool(packs)
    rules: list[Rule] = []
    ids: dict[str, str] = {}
    for relative, path in sorted(discovered.items()):
        rule_id, name, severity, query_languages, tags = _validate_policy(path, relative)
        if rule_id in ids:
            raise InventoryError(f"duplicate rule ID {rule_id!r} in {ids[rule_id]} and {relative}")
        ids[rule_id] = relative
        metadata = metadata_by_path.get(relative, {})
        declared_id = metadata.get("id")
        if declared_id is not None and declared_id != rule_id:
            raise InventoryError(
                f"manifest ID {declared_id!r} does not match policy ID {rule_id!r} in {relative}"
            )
        rules.append(
            Rule(
                path=relative,
                name=name,
                rule_id=rule_id,
                severity=severity,
                pack_id=metadata.get("pack_id"),
                category=metadata.get("category") if manifest_mode else None,
                supported_languages=metadata.get("supported_languages") if manifest_mode else None,
                activation=metadata.get("activation") if manifest_mode else None,
                query_languages=query_languages,
                tags=tags,
            )
        )

    rule_by_path = {rule.path: rule for rule in rules}
    case_counts = _load_case_counts(root, rule_by_path)
    language_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    activation_counts: Counter[str] = Counter()
    inline_language_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    for rule in rules:
        severity_counts[rule.severity or "unspecified"] += 1
        if rule.supported_languages is not None:
            language_counts.update(rule.supported_languages)
        if manifest_mode:
            category_counts[rule.category or "unspecified"] += 1
            activation_counts[rule.activation or "unspecified"] += 1
        if not manifest_mode:
            inline_language_counts.update(rule.query_languages)
            tag_counts.update(rule.tags)

    pack_counts = Counter(rule.pack_id for rule in rules if rule.pack_id is not None)
    if manifest_mode:
        pack_counts.update({pack_id: 0 for pack_id in packs})
    family_counts = Counter(PurePosixPath(rule.path).parts[1] for rule in rules if rule.pack_id is None)
    pack_details = []
    for pack_id, count in sorted(pack_counts.items()):
        detail = packs[pack_id]
        pack_details.append({"id": pack_id, "name": detail["name"], "path": detail["path"], "policy_count": count})

    policies = []
    for rule in rules:
        item: dict[str, Any] = {
            "id": rule.rule_id,
            "name": rule.name,
            "path": rule.path,
            "pack_id": rule.pack_id,
            "category": rule.category,
            "severity": rule.severity,
            "supported_languages": list(rule.supported_languages) if rule.supported_languages is not None else None,
            "query_languages": list(rule.query_languages),
            "tags": list(rule.tags),
            "activation": rule.activation,
        }
        if rule.path in case_counts:
            item["recorded_case_expectations"] = case_counts[rule.path]
        policies.append(item)

    result: dict[str, Any] = {
        "schema_version": 1,
        "metadata_mode": "manifest" if manifest_mode else "generic",
        "summary": {
            "policy_count": len(rules),
            "unique_rule_id_count": len(ids),
            "pack_count": len(pack_counts) if manifest_mode else None,
            "packs": pack_details,
            "authoring_family_counts": dict(sorted(family_counts.items())) if not manifest_mode else None,
            "categories": dict(sorted(category_counts.items())),
            "severities": dict(sorted(severity_counts.items())),
            "declared_language_policy_counts": dict(sorted(language_counts.items())) if manifest_mode else None,
            "declared_language_policy_pair_count": sum(language_counts.values()) if manifest_mode else None,
            "declared_language_count": len(language_counts) if manifest_mode else None,
            "activation_counts": dict(sorted(activation_counts.items())) if manifest_mode else None,
            "inline_query_language_policy_counts": dict(sorted(inline_language_counts.items())) if not manifest_mode else None,
            "tag_policy_counts": dict(sorted(tag_counts.items())) if not manifest_mode else None,
            "case_expectation_count": sum(sum(counts.values()) for counts in case_counts.values()),
            "case_expectation_policy_count": len(case_counts),
        },
        "policies": policies,
    }
    return result


def _md(value: Any) -> str:
    text = str(value)
    return (
        text.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "<br>")
        .replace("|", "\\|")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def _case_label(counts: dict[str, int] | None) -> str:
    if not counts:
        return ""
    return f"positive expected: {counts.get('positive', 0)}; zero expected: {counts.get('zero_expected', 0)}"


def render_summary(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    manifest_mode = inventory["metadata_mode"] == "manifest"
    count = summary["unique_rule_id_count"]
    suffix = f" across {summary['pack_count']} policy packs" if manifest_mode else ""
    lines = [f"**{count} unique rules{suffix}.**", ""]
    dimensions: list[tuple[str, dict[str, int]]] = []
    if manifest_mode:
        dimensions.extend([
            ("Pack", {pack["id"]: pack["policy_count"] for pack in summary["packs"]}),
            ("Category", summary["categories"]),
        ])
    else:
        dimensions.append(("Authoring family", summary["authoring_family_counts"]))
    dimensions.append(("Severity", summary["severities"]))
    lines.extend(["| Breakdown | Value | Rules |", "| --- | --- | ---: |"])
    for label, counts in dimensions:
        for name, amount in counts.items():
            lines.append(f"| {label} | {_md(name)} | {amount} |")
    if manifest_mode:
        counts = summary["declared_language_policy_counts"] or {}
        language_label = "Manifest supported language"
        lines.extend([
            "", "Languages are explicit manifest declarations; a rule may appear in multiple rows.",
            f"{summary['declared_language_count']} declared languages; "
            f"{summary['declared_language_policy_pair_count']} rule-language pairs.",
        ])
    else:
        counts = summary["inline_query_language_policy_counts"] or {}
        language_label = "Inline query language scope"
        lines.extend([
            "", "Language support is undeclared. These query scopes describe syntax, "
            "including C queries using the `cpp` grammar; they do not establish source-language support.",
        ])
    lines.extend(["", f"| {language_label} | Rules |", "| --- | ---: |"])
    lines.extend(f"| {_md(name)} | {amount} |" for name, amount in counts.items())
    if not counts:
        lines.append("| Unspecified | 0 |")
    lines.append("")
    if manifest_mode:
        labels = ", ".join(f"{_md(name)} {amount}" for name, amount in summary["activation_counts"].items())
        lines.append(f"Activation labels: {labels}. Omitted labels remain unspecified.")
    else:
        tags = summary["tag_policy_counts"] or {}
        if tags:
            lines.append("Topic tags (overlapping): " + ", ".join(
                f"{_md(name)} {amount}" for name, amount in tags.items()
            ) + ".")
    if summary["case_expectation_count"]:
        positive = sum(policy.get("recorded_case_expectations", {}).get("positive", 0)
                       for policy in inventory["policies"])
        zero = summary["case_expectation_count"] - positive
        lines.append(
            f"Recorded case expectations: {summary['case_expectation_count']} across "
            f"{summary['case_expectation_policy_count']} rules ({positive} positive, {zero} zero expected). "
            "These counts describe fixtures, not executed test results."
        )
    lines.extend([
        "Metadata is an inventory, not evidence of enablement or behavior qualification.",
        "[Full rule catalog](docs/rule-catalog.md).",
    ])
    return "\n".join(lines) + "\n"


def render_catalog(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    manifest_mode = inventory["metadata_mode"] == "manifest"
    lines = ["# Rule catalog", ""]
    source_count = (
        f"{summary['pack_count']} manifest packs"
        if manifest_mode
        else f"{len(summary['authoring_family_counts'])} authoring families"
    )
    lines.append(f"This catalog lists {summary['unique_rule_id_count']} unique rule IDs from {source_count}.")
    if manifest_mode:
        lines.append(
            "Supported languages come only from each rule's manifest declaration. Language counts overlap "
            "when one policy declares multiple languages. These declarations do not establish tested, enabled, "
            "or qualified behavior."
        )
    else:
        lines.append(
            "This repository has no policy manifests. Declared language support and primary category are "
            "unknown; inline query language scopes are shown separately and do not establish support."
        )
        if summary["tag_policy_counts"]:
            lines.append(
                "Tags are author metadata only: "
                + ", ".join(f"{_md(tag)} {count}" for tag, count in summary["tag_policy_counts"].items())
                + "."
            )
    if summary["case_expectation_count"]:
        lines.append(
            "Case figures count JSON expected-finding declarations only: a nonempty expected_findings list is "
            "counted as positive and an empty list as zero expected. They do not report runtime test results."
        )
    columns = ["Policy", "Stable ID", "Manifest support / query scopes", "Category", "Severity"]
    if summary["case_expectation_count"]:
        columns.append("Recorded case expectations")
    lines.extend(["", "| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"])
    for policy in inventory["policies"]:
        display_path = "../" + quote(policy["path"], safe="/._-")
        name = _md(policy["name"])
        linked_name = f"[{name}]({display_path})"
        support = policy["supported_languages"]
        if support is not None:
            support_text = ", ".join(support) if support else "None (empty declaration)"
        else:
            query = ", ".join(policy["query_languages"]) or "none"
            support_text = f"Undeclared; query: {query}"
        category = policy["category"] or "unspecified"
        severity = policy["severity"] or "unspecified"
        row = [linked_name, f"`{_md(policy['id'])}`", _md(support_text), _md(category), _md(severity)]
        if summary["case_expectation_count"]:
            row.append(_md(_case_label(policy.get("recorded_case_expectations")) or "unrecorded"))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def _readme_with_summary(readme: str, summary: str) -> str:
    if readme.count(README_START) != 1 or readme.count(README_END) != 1:
        raise InventoryError("README.md must contain exactly one rule-stats start and end marker")
    start = readme.index(README_START)
    end = readme.index(README_END)
    if end < start:
        raise InventoryError("README.md rule-stats markers are out of order")
    after_start = start + len(README_START)
    return readme[:after_start] + "\n" + summary.rstrip() + "\n" + readme[end:]


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
            temporary = handle.name
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def _run(args: argparse.Namespace) -> int:
    root = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parents[1]
    inventory = build_inventory(root)
    summary = render_summary(inventory)
    catalog = render_catalog(inventory)

    if args.json:
        print(json.dumps(inventory, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    if args.check:
        readme_path = root / "README.md"
        if not readme_path.is_file():
            raise InventoryError("README.md is required for --check")
        readme = readme_path.read_text(encoding="utf-8")
        expected_readme = _readme_with_summary(readme, summary)
        # Check the exact current block without changing either artifact.
        actual = readme[readme.index(README_START) : readme.index(README_END) + len(README_END)]
        expected = expected_readme[
            expected_readme.index(README_START) : expected_readme.index(README_END) + len(README_END)
        ]
        if actual != expected:
            raise InventoryError("README.md rule-stats block is stale")
        catalog_path = root / "docs" / "rule-catalog.md"
        try:
            existing_catalog = catalog_path.read_text(encoding="utf-8")
        except OSError:
            existing_catalog = None
        if existing_catalog != catalog:
            raise InventoryError("docs/rule-catalog.md is stale or missing")
        print("rule inventory artifacts are up to date")
        return 0
    if args.write:
        readme_path = root / "README.md"
        if not readme_path.is_file():
            raise InventoryError("README.md is required for --write")
        readme = readme_path.read_text(encoding="utf-8")
        updated_readme = _readme_with_summary(readme, summary)
        _atomic_write(readme_path, updated_readme)
        _atomic_write(root / "docs" / "rule-catalog.md", catalog)
    print(summary, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write", action="store_true", help="update the marked README block and catalog")
    modes.add_argument("--check", action="store_true", help="fail if generated artifacts are stale")
    modes.add_argument("--json", action="store_true", help="print the deterministic JSON inventory")
    parser.add_argument("--repo", help="repository root (defaults to the repository containing this script)")
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except InventoryError as error:
        print(f"rule_stats.py: error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
