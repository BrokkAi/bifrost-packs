"""Generate the reviewed Ruby models for the Bifrost 0.15.2 CVE leads.

Writes semantic-packs/ruby/bifrost.ruby.rexml.json,
semantic-packs/ruby/bifrost.ruby.net-imap.json and
semantic-packs/ruby/bifrost.ruby.rubygems-installer.json.

Each version-gated pack declares the same API in several member shards. Every
member shard activates from one Gemfile.lock version range, and its member ids
name that range, so a policy can select the affected declarations by exact
member id. Types use Bifrost's canonical type id and sit in one shared shard.
Run from the repository root: python3 research/osv-dataflow-2026-11/ruby-0152/generator/genmodels.py
"""

import hashlib
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "semantic-packs" / "ruby"

UNTYPED = {"kind": "named", "name": "untyped"}


def param(name, optional=False):
    entry = {"name": name, "type": UNTYPED}
    if optional:
        entry["optional"] = True
    return entry


def canonical_type_id(name, ecosystem="rubygems"):
    """Bifrost's external-declaration type id (semantic_model::identity::type_declaration_id).

    A Ruby constant receiver binds to a model type only through this id, so a
    model type must not use a hand-picked id. Framing: each value is a
    big-endian u64 length then its bytes; a field is its name then its value.
    """
    digest = hashlib.sha256()
    for value in (b"bifrost.external-declaration.type.v1", b"ecosystem", ecosystem.encode(), b"name", name.encode()):
        digest.update(struct.pack(">Q", len(value)))
        digest.update(value)
    return "type." + digest.hexdigest()


def type_decl(type_id, name, path):
    return {
        "id": type_id,
        "name": name,
        "type_kind": "class",
        "visibility": "public",
        "hierarchy": [],
        "locator": {"kind": "artifact", "path": path, "symbol": name},
    }


def member(member_id, owner, owner_name, name, path, params, static, returns=None):
    signature = {"parameters": params}
    if returns is not None:
        signature["returns"] = {"kind": "declared", "id": returns}
    return {
        "id": member_id,
        "owner": owner,
        "name": name,
        "member_kind": "method",
        "visibility": "public",
        "is_static": static,
        "callable_family_complete": True,
        "aliases": [],
        "locator": {"kind": "artifact", "path": path, "symbol": f"{owner_name}.{name}"},
        "signature": signature,
    }


NETWORK_IO = {"id": "bifrost.network_io", "timing": "immediate", "certainty": "definite"}
POSSIBLE_NETWORK_IO = {"id": "bifrost.network_io", "timing": "unknown", "certainty": "possible"}
# Argument 0 flows to the return value (Gem::Installer.at wraps the archive it is given).
PARAM0_TO_RETURN = {"input": {"kind": "parameter", "ordinal": 0}, "exit_kind": "normal", "output": {"kind": "normal_return"}}


def summaries(prefix, owner_name, name, path, params, transfers=(), effects=()):
    """One summary per accepted arity, with the given transfers and declared effects."""
    required = [p for p in params if not p.get("optional")]
    out = []
    for count in range(len(required), len(params) + 1):
        names = ", ".join(p["name"] for p in params[:count])
        out.append(
            {
                "id": f"summary.{prefix}.{name}-{count}",
                "target": {
                    "path": path,
                    "symbol": f"{owner_name}.{name}({names})",
                    "has_receiver": True,
                    "parameter_count": count,
                },
                "completeness": "complete",
                "covers_overrides": True,
                "locations": [],
                "transfers": list(transfers),
                "effects": [],
                "declared_effects": list(effects),
            }
        )
    return out


def activation(gem, ranges):
    if ranges is None:
        return [{"targets": [], "configurations": []}]
    return [{"targets": [], "configurations": [], "package": {"name": gem, "version": r}} for r in ranges]


def pack(pack_id, version, source, revision, shards):
    return {
        "schema_version": 2,
        "pack_id": pack_id,
        "version": version,
        "producer": {"name": "bifrost-reviewed-ruby-models", "version": "1.0.0"},
        "language": "ruby",
        "ecosystem": "rubygems",
        "compatibility": {"bifrost": ">=0.15.2, <1.0.0", "toolchains": []},
        "provenance": {"source": source, "revision": revision},
        "license": "Apache-2.0",
        "completeness": "complete",
        "safety": {"generated_code_only": False, "review_required": False},
        "shards": shards,
    }


def gated_pack(pack_id, version, source, revision, gem, slug, ranges, api, behavior=None):
    """api: list of (owner_name, path, [(name, params, static, returns_self)]).

    behavior maps a method name to {"transfers": [...], "effects": [...]} for its
    summaries; every other method is summarized with no transfers or effects.

    Types carry Bifrost's canonical id, which is the same for every version, so
    they live in one shard that activates for the union of the ranges. Each
    version split then has its own member shard whose member ids name the split.
    Summaries are keyed by locator, not member id, so one summaries shard serves
    every split.
    """
    union = [entry for _split, split_ranges in ranges for entry in activation(gem, split_ranges)]
    types = [type_decl(canonical_type_id(owner_name), owner_name, path) for owner_name, path, _methods in api]
    shards = [
        {
            "id": f"types.{slug}",
            "activation": union,
            "payload": {"kind": "declaration_facts", "types": types, "members": [], "relations": []},
        }
    ]
    for split, split_ranges in ranges:
        prefix = f"{slug}.{split}"
        members = []
        for owner_name, path, methods in api:
            owner_slug = owner_name.lower().replace("::", "-")
            type_id = canonical_type_id(owner_name)
            for name, params, static, returns_self in methods:
                member_id = f"member.{prefix}.{owner_slug}.{name}"
                members.append(
                    member(member_id, type_id, owner_name, name, path, params, static, type_id if returns_self else None)
                )
        shards.append(
            {
                "id": f"members.{prefix}",
                "activation": activation(gem, split_ranges),
                "payload": {"kind": "declaration_facts", "types": [], "members": members, "relations": []},
            }
        )
    sums = []
    for owner_name, path, methods in api:
        owner_slug = owner_name.lower().replace("::", "-")
        for name, params, _static, _returns in methods:
            extra = (behavior or {}).get(name, {})
            sums.extend(
                summaries(
                    f"{slug}.{owner_slug}",
                    owner_name,
                    name,
                    path,
                    params,
                    extra.get("transfers", ()),
                    extra.get("effects", ()),
                )
            )
    shards.append({"id": f"summaries.{slug}", "activation": union, "payload": {"kind": "procedure_summaries", "summaries": sums}})
    return pack(pack_id, version, source, revision, shards)


REXML_API = [
    ("REXML::Document", "rexml/document.rb", [("new", [param("source", True), param("context", True)], True, True)]),
]

# Ranges are OSV's: CVE-2024-35176 (GHSA-vg3r-rm7w-2xgh) fixed 3.2.7;
# CVE-2025-58767 (GHSA-c2f4-jgmc-q2r5) introduced 3.3.3, fixed 3.4.2.
REXML_RANGES = [
    ("cve-2024-35176", ["<3.2.7"]),
    ("cve-2025-58767", [">=3.3.3, <3.4.2"]),
    ("unaffected", [">=3.2.7, <3.3.3", ">=3.4.2"]),
]

IMAP_API = [
    (
        "Net::IMAP",
        "net/imap.rb",
        [
            ("new", [param("host"), param("port_or_options", True)], True, True),
            ("login", [param("user"), param("password")], False, False),
            ("select", [param("mailbox")], False, False),
            ("examine", [param("mailbox")], False, False),
            ("logout", [], False, False),
            ("disconnect", [], False, False),
            ("search", [param("keys"), param("charset", True)], False, False),
            ("uid_search", [param("keys"), param("charset", True)], False, False),
            ("sort", [param("sort_keys"), param("search_keys"), param("charset")], False, False),
            ("uid_sort", [param("sort_keys"), param("search_keys"), param("charset")], False, False),
            ("thread", [param("algorithm"), param("search_keys"), param("charset")], False, False),
            ("uid_thread", [param("algorithm"), param("search_keys"), param("charset")], False, False),
            ("fetch", [param("set"), param("attr"), param("mod", True)], False, False),
            ("uid_fetch", [param("set"), param("attr"), param("mod", True)], False, False),
        ],
    )
]

# CVE-2026-47240 (GHSA-8p34-64r3-mwg8) and CVE-2026-47241 (GHSA-c4fp-cxrr-mj66)
# share one OSV range: introduced 0 fixed 0.5.15, introduced 0.6.0 fixed 0.6.4.1.
IMAP_RANGES = [
    ("affected", ["<0.5.15", ">=0.6.0, <0.6.4"]),
    ("unaffected", [">=0.5.15, <0.6.0", ">=0.6.5"]),
]

INSTALLER_API = [
    ("Gem::Installer", "rubygems/installer.rb", [
            ("at", [param("path"), param("options", True)], True, True),
            ("install", [], False, False),
        ]),
]


def write(name, data):
    path = OUT / name
    path.write_text(json.dumps(data, indent=1) + "\n")
    print(path.relative_to(ROOT))


def main():
    write(
        "bifrost.ruby.rexml.json",
        gated_pack(
            "bifrost.ruby.rexml",
            "0.1.0",
            "ruby/rexml REXML::Document.new(source = nil, context = {}) in lib/rexml/document.rb, identical across 3.2.6, 3.2.7, 3.4.1 and 3.4.2; OSV GHSA-vg3r-rm7w-2xgh and GHSA-c2f4-jgmc-q2r5 version ranges",
            "rexml 3.2.6, 3.2.7, 3.4.1, 3.4.2",
            "rexml",
            "ruby.rexml",
            REXML_RANGES,
            REXML_API,
        ),
    )
    write(
        "bifrost.ruby.net-imap.json",
        gated_pack(
            "bifrost.ruby.net-imap",
            "0.1.0",
            "ruby/net-imap Net::IMAP.new, login, select, examine, logout, disconnect and the search, uid_search, sort, uid_sort, thread, uid_thread, fetch and uid_fetch commands in lib/net/imap.rb (0.5.x and 0.6.x); OSV GHSA-8p34-64r3-mwg8 and GHSA-c4fp-cxrr-mj66 version ranges",
            "net-imap 0.5.14, 0.5.15, 0.6.4, 0.6.4.1",
            "net-imap",
            "ruby.net-imap",
            IMAP_RANGES,
            IMAP_API,
            # Every modeled Net::IMAP method opens, uses or closes the server connection.
            {name: {"effects": [NETWORK_IO]} for name, *_ in IMAP_API[0][2]},
        ),
    )
    write(
        "bifrost.ruby.rubygems-installer.json",
        gated_pack(
            "bifrost.ruby.rubygems-installer",
            "0.1.0",
            "rubygems Gem::Installer.at(path, options = {}) and Gem::Installer#install in lib/rubygems/installer.rb. On every RubyGems release Gem::Installer.at wraps the archive at path (Gem::Package.new) in an installer, and #install unpacks it and runs its extension builds and plugins, so #install may perform any effect, network I/O included",
            "rubygems 3.5",
            "rubygems",
            "ruby.rubygems-installer",
            [("all", None)],
            INSTALLER_API,
            # #install runs the gem's extension builds and plugins, which may do
            # anything, so its summary declares possible network I/O at an unknown
            # time instead of an empty effect set that would close coverage.
            {"at": {"transfers": [PARAM0_TO_RETURN]}, "install": {"effects": [POSSIBLE_NETWORK_IO]}},
        ),
    )


if __name__ == "__main__":
    main()
