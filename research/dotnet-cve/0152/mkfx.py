"""Stage the bifrost-packs#167 fixture workspaces from the reviewed models.

Each case directory under the fixture is its own workspace: its own restored
NuGet evidence (obj/project.assets.json plus a stub package assembly), its own
copy of the reviewed models and of the policy. Source files are written by hand
and kept; this script only (re)writes the generated evidence and copies.
Usage: python3 research/dotnet-cve/0152/mkfx.py <stub dll>
"""

import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures/policy/bifrost.security/csharp-webassembly-debugging-affected-version"
POLICY = ROOT / "rules/bifrost.security/policies/csharp/webassembly-debugging-affected-version.rqlp"
MODELS = [
    ROOT / "semantic-packs/dotnet/bifrost.dotnet.aspnetcore-hosting-csharp.json",
    ROOT / "semantic-packs/dotnet/bifrost.dotnet.aspnetcore-webassembly-server-csharp.json",
]
PACKAGE = "Microsoft.AspNetCore.Components.WebAssembly.Server"
# case directory -> restored package version, or None for no restore output
CASES = {
    "affected": "8.0.31",
    "fixed": "8.0.32",
    "incomplete/minimal-hosting": "9.0.20",
    "incomplete/lookalike": "8.0.31",
    "incomplete/unrestored": None,
}


def csproj(version):
    reference = f'\n  <ItemGroup>\n    <PackageReference Include="{PACKAGE}" Version="{version}" />\n  </ItemGroup>' if version else ""
    return (
        '<Project Sdk="Microsoft.NET.Sdk.Web">\n  <PropertyGroup>\n    <TargetFramework>net8.0</TargetFramework>\n'
        f"  </PropertyGroup>{reference}\n</Project>\n"
    )


def assets(version):
    dll = f"lib/net8.0/{PACKAGE}.dll"
    key = f"{PACKAGE}/{version}"
    return {
        "version": 3,
        "targets": {"net8.0": {key: {"type": "package", "compile": {dll: {}}, "runtime": {dll: {}}}}},
        "libraries": {key: {"type": "package", "path": f"{PACKAGE.lower()}/{version}", "files": [dll]}},
        "projectFileDependencyGroups": {"net8.0": [f"{PACKAGE} >= {version}"]},
        "packageFolders": {".nuget/packages/": {}},
        "project": {
            "version": "1.0.0",
            "restore": {
                "projectUniqueName": "App.csproj",
                "projectName": "App",
                "projectPath": "App.csproj",
                "packagesPath": ".nuget/packages/",
                "outputPath": "obj/",
                "projectStyle": "PackageReference",
                "originalTargetFrameworks": ["net8.0"],
                "frameworks": {"net8.0": {"targetAlias": "net8.0", "projectReferences": {}}},
            },
            "frameworks": {
                "net8.0": {"targetAlias": "net8.0", "dependencies": {PACKAGE: {"target": "Package", "version": f"[{version}, )"}}}
            },
        },
    }


def main(stub):
    for case, version in CASES.items():
        root = FIXTURE / case
        for generated in ("obj", ".nuget", ".bifrost"):
            shutil.rmtree(root / generated, ignore_errors=True)
        (root / ".bifrost/semantic-models").mkdir(parents=True)
        (root / ".bifrost/policies").mkdir()
        (root / ".bifrost/packs.json").write_text(json.dumps({"schema_version": 1, "ecosystems": ["dotnet"]}) + "\n")
        for model in MODELS:
            shutil.copy(model, root / ".bifrost/semantic-models" / model.name)
        shutil.copy(POLICY, root / ".bifrost/policies" / POLICY.name)
        (root / "App.csproj").write_text(csproj(version))
        if version:
            (root / "obj").mkdir()
            (root / "obj/project.assets.json").write_text(json.dumps(assets(version), indent=2) + "\n")
            lib = root / ".nuget/packages" / PACKAGE.lower() / version / "lib/net8.0"
            lib.mkdir(parents=True)
            shutil.copy(stub, lib / f"{PACKAGE}.dll")


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]))
