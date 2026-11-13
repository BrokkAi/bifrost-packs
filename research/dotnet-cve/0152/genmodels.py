"""Generate the reviewed C# models for bifrost-packs#167 (CVE-2026-96230).

Writes semantic-packs/dotnet/bifrost.dotnet.aspnetcore-hosting-csharp.json and
semantic-packs/dotnet/bifrost.dotnet.aspnetcore-webassembly-server-csharp.json.

The hosting pack declares the minimal-hosting entry points of the ASP.NET Core
shared framework (WebApplication.CreateBuilder, WebApplicationBuilder.Build and
WebApplication's IApplicationBuilder interface) so that `var app =
builder.Build()` has a declared receiver type. The WebAssembly.Server pack
declares UseWebAssemblyDebugging twice: one shard per side of the fix, each
activated by restored NuGet evidence for its version ranges.
Run from the repository root: python3 research/dotnet-cve/0152/genmodels.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "semantic-packs" / "dotnet"


def named(name):
    return {"kind": "named", "name": name, "arguments": [], "nullable": False}


VOID = named("System.Void")


def type_decl(type_id, name, assembly, kind="class", hierarchy=(), sealed=False, static=False):
    return {
        "id": type_id,
        "name": name,
        "type_kind": kind,
        "visibility": "public",
        "is_abstract": kind == "interface" or static,
        "is_sealed": sealed or static,
        "type_parameters": [],
        "hierarchy": [{"hierarchy_kind": k, "target": named(t)} for k, t in hierarchy],
        "locator": {"kind": "artifact", "path": assembly, "symbol": name},
    }


def method(member_id, owner, owner_name, name, assembly, params, returns, static, receiver=None):
    entry = {
        "id": member_id,
        "owner": owner,
        "name": name,
        "member_kind": "method",
        "visibility": "public",
        "is_static": static,
        "callable_family_complete": True,
        "locator": {"kind": "artifact", "path": assembly, "symbol": f"{owner_name}.{name}"},
        "signature": {
            "type_parameters": [],
            "parameters": [{"name": n, "type": t} for n, t in params],
            "returns": returns,
        },
    }
    if receiver is not None:
        entry["extension_receiver"] = receiver
    return entry


def pack(pack_id, source, revision, shards):
    return {
        "schema_version": 2,
        "pack_id": pack_id,
        "version": "0.1.0",
        "producer": {"name": "bifrost-reviewed-dotnet-models", "version": "0.1.0"},
        "language": "csharp",
        "ecosystem": "nuget",
        "compatibility": {"bifrost": ">=0.15.2, <1.0.0", "toolchains": []},
        "provenance": {"source": source, "revision": revision},
        "license": "Apache-2.0",
        "completeness": "complete",
        "safety": {"generated_code_only": False, "review_required": False},
        "shards": shards,
    }


def hosting():
    asm = "Microsoft.AspNetCore.dll"
    p = "type.dotnet.aspnetcore-hosting-csharp."
    m = "member.dotnet.aspnetcore-hosting-csharp."
    app_builder = "Microsoft.AspNetCore.Builder.IApplicationBuilder"
    web_app = "Microsoft.AspNetCore.Builder.WebApplication"
    web_builder = "Microsoft.AspNetCore.Builder.WebApplicationBuilder"
    types = [
        type_decl(p + "iapplicationbuilder", app_builder, "Microsoft.AspNetCore.Http.Abstractions.dll", kind="interface"),
        type_decl(p + "webapplication", web_app, asm, hierarchy=[("implements", app_builder)], sealed=True),
        type_decl(p + "webapplicationbuilder", web_builder, asm, sealed=True),
        type_decl(p + "webapplicationoptions", "Microsoft.AspNetCore.Builder.WebApplicationOptions", asm),
    ]
    string_array = {"kind": "array", "element": named("System.String")}
    members = [
        method(m + "webapplication.createbuilder.0", p + "webapplication", web_app, "CreateBuilder", asm, [], named(web_builder), True),
        method(m + "webapplication.createbuilder.args", p + "webapplication", web_app, "CreateBuilder", asm, [("args", string_array)], named(web_builder), True),
        method(
            m + "webapplication.createbuilder.options",
            p + "webapplication",
            web_app,
            "CreateBuilder",
            asm,
            [("options", named("Microsoft.AspNetCore.Builder.WebApplicationOptions"))],
            named(web_builder),
            True,
        ),
        method(m + "webapplicationbuilder.build", p + "webapplicationbuilder", web_builder, "Build", asm, [], named(web_app), False),
    ]
    return pack(
        "bifrost.dotnet.aspnetcore-hosting-csharp",
        "ASP.NET Core shared framework (Microsoft.AspNetCore.App) reference assemblies: WebApplication.CreateBuilder overloads, WebApplicationBuilder.Build and WebApplication's IApplicationBuilder implementation; identical in .NET 8, 9 and 10",
        "Microsoft.AspNetCore.App 8.0, 9.0, 10.0",
        [
            {
                "id": "declarations.dotnet.aspnetcore-hosting-csharp",
                "activation": [{"targets": [], "configurations": []}],
                "payload": {"kind": "declaration_facts", "types": types, "members": members, "relations": []},
            }
        ],
    )


# OSV GHSA-qjpx-jqm5-h2c4: introduced 8.0.0 fixed 8.0.32, 9.0.0 fixed 9.0.21,
# 10.0.0 fixed 10.0.13, 11.0.0-preview.1 fixed 11.0.0-rc.2. Versions before 8.0.0
# are outside the advisory record and activate neither shard.
WASM_RANGES = [
    ("affected", [">=8.0.0, <8.0.32", ">=9.0.0, <9.0.21", ">=10.0.0, <10.0.13", ">=11.0.0-preview.1, <11.0.0-rc.2"]),
    ("fixed", [">=8.0.32, <9.0.0", ">=9.0.21, <10.0.0", ">=10.0.13, <11.0.0-preview.1", ">=11.0.0-rc.2"]),
]


def wasm_server():
    package = "Microsoft.AspNetCore.Components.WebAssembly.Server"
    asm = package + ".dll"
    owner_name = "Microsoft.AspNetCore.Builder.WebAssemblyNetDebugProxyAppBuilderExtensions"
    receiver = named("Microsoft.AspNetCore.Builder.IApplicationBuilder")
    shards = []
    for split, ranges in WASM_RANGES:
        prefix = f"dotnet.aspnetcore-webassembly-server-csharp.{split}"
        owner = f"type.{prefix}.webassemblynetdebugproxyappbuilderextensions"
        shards.append(
            {
                "id": f"declarations.{prefix}",
                "activation": [{"package": {"name": package, "version": r}} for r in ranges],
                "payload": {
                    "kind": "declaration_facts",
                    "types": [type_decl(owner, owner_name, asm, static=True)],
                    "members": [
                        method(
                            f"member.{prefix}.usewebassemblydebugging",
                            owner,
                            owner_name,
                            "UseWebAssemblyDebugging",
                            asm,
                            [("app", receiver)],
                            VOID,
                            True,
                            receiver=receiver,
                        )
                    ],
                    "relations": [],
                },
            }
        )
    return pack(
        "bifrost.dotnet.aspnetcore-webassembly-server-csharp",
        "dotnet/aspnetcore src/Components/WebAssembly/Server WebAssemblyNetDebugProxyAppBuilderExtensions.UseWebAssemblyDebugging(this IApplicationBuilder app), unchanged across the 8.0, 9.0 and 10.0 servicing branches; OSV GHSA-qjpx-jqm5-h2c4 version ranges. Two shards declare the same API, one per side of the fix.",
        "Microsoft.AspNetCore.Components.WebAssembly.Server 8.0.31, 8.0.32, 9.0.20, 9.0.21, 10.0.12, 10.0.13",
        shards,
    )


def write(name, data):
    path = OUT / name
    path.write_text(json.dumps(data, indent=1) + "\n")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    write("bifrost.dotnet.aspnetcore-hosting-csharp.json", hosting())
    write("bifrost.dotnet.aspnetcore-webassembly-server-csharp.json", wasm_server())
