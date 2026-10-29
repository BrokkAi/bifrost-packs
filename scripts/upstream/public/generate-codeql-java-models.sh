#!/usr/bin/env bash
set -euo pipefail

# The released engine pin does not yet include codeql-jvm-catalogs or
# codeql-jdk-summaries. Set BIFROST_SEMANTIC_PACK_GENERATOR to the compatible
# generator executable; bump the engine pin only when that follow-up release
# is available.
if [[ $# -ne 1 ]]; then
  echo "usage: $0 SCRATCH_DIR" >&2
  exit 2
fi

scratch=$(realpath -m "$1")
repository_root=$(CDPATH='' cd -- "$(dirname -- "$0")/../../.." && pwd)
generator=${BIFROST_SEMANTIC_PACK_GENERATOR:?set BIFROST_SEMANTIC_PACK_GENERATOR}
codeql_ext=${CODEQL_JAVA_EXT:?set CODEQL_JAVA_EXT to java/ql/lib/ext}
java_home=${JAVA_HOME:?set JAVA_HOME to pinned Temurin JDK 21}
codeql_commit=ae741615f3e178ce61289a651790dc67fcc18e19
java_release=21+35-LTS
jdk_modules_sha256=1465b683efd50adb60af815a8554129f8bd1b03807444cc491a5d2800d6f2091

[[ -x "$generator" ]] || { echo "generator is not executable: $generator" >&2; exit 2; }
[[ -d "$codeql_ext" ]] || { echo "CodeQL extension directory is missing: $codeql_ext" >&2; exit 2; }
[[ $(git -C "$codeql_ext" rev-parse HEAD) == "$codeql_commit" ]] || {
  echo "CodeQL checkout does not match pinned commit $codeql_commit" >&2
  exit 2
}
[[ -f "$java_home/release" ]] || { echo "JDK release file is missing: $java_home/release" >&2; exit 2; }
grep -Fx "JAVA_RUNTIME_VERSION=\"$java_release\"" "$java_home/release" >/dev/null || {
  echo "expected Temurin JAVA_RUNTIME_VERSION=$java_release" >&2
  exit 2
}
echo "$jdk_modules_sha256  $java_home/lib/modules" | shasum -a 256 --check --status || {
  echo "JDK module image does not match pinned Temurin $java_release" >&2
  exit 2
}

work="$scratch/generated"
download="$scratch/downloads"
mkdir -p "$work/jdk" "$work/servlet" "$work/summary" "$download"
fetch_jar() {
  local file=$1 url=$2 sha256=$3
  if [[ ! -f "$download/$file" ]]; then
    curl --fail --location --silent --show-error --retry 5 --retry-delay 5 \
      --connect-timeout 30 --output "$download/$file" "$url"
  fi
  echo "$sha256  $download/$file" | sha256sum --check --status || {
    echo "downloaded JAR does not match pinned SHA-256: $file" >&2
    exit 1
  }
}

javax_jar=javax.servlet-api-4.0.1.jar
jakarta_jar=jakarta.servlet-api-6.0.0.jar
fetch_jar "$javax_jar" \
  https://repo.maven.apache.org/maven2/javax/servlet/javax.servlet-api/4.0.1/javax.servlet-api-4.0.1.jar \
  83a03dd877d3674576f0da7b90755c8524af099ccf0607fc61aa971535ad7c60
fetch_jar "$jakarta_jar" \
  https://repo.maven.apache.org/maven2/jakarta/servlet/jakarta.servlet-api/6.0.0/jakarta.servlet-api-6.0.0.jar \
  c034eb1afb158987dbb53a5fea0cadf611c8dae8daadd59c44d9d5ab70129cef

"$generator" codeql-jvm-catalogs "$codeql_ext" "$codeql_commit" jdk 1 \
  "$work/jdk/catalogs" "$work/jdk/report.json" --java-home "$java_home"
"$generator" codeql-jvm-catalogs "$codeql_ext" "$codeql_commit" servlet 1 \
  "$work/servlet/catalogs" "$work/servlet/report.json" \
  --jar "$download/$javax_jar" --jar "$download/$jakarta_jar"
"$generator" codeql-jdk-summaries "$codeql_ext" "$codeql_commit" \
  "$java_home" "$work/summary/bifrost.java-codeql-jdk-summaries.json" \
  "$work/summary/report.json"

python3 - "$repository_root" "$work" <<'PY'
import json
import shutil
import sys
from pathlib import Path

root, work = map(Path, sys.argv[1:])
rule = root / "rules/bifrost.java-codeql-security"
scope = root / "fixtures/codeql_gate/java"
semantic = root / "semantic-packs/jvm/codeql"
for directory in (rule / "catalogs", rule / "generation-summaries", scope, semantic):
    directory.mkdir(parents=True, exist_ok=True)

jdk = json.loads((work / "jdk/report.json").read_text())
servlet = json.loads((work / "servlet/report.json").read_text())
catalogs = []
combined = set()
for name, metadata in sorted(jdk["catalogs"].items()):
    shutil.copyfile(work / "jdk/catalogs" / f"{name}.json", rule / "catalogs" / f"{name}.json")
    catalogs.append({"path": f"catalogs/{name}.json", "semantic_hash": metadata["semantic_hash"]})
    rows = jdk["rows_by_catalog"].get(name, [])
    (scope / f"{name}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    if name.startswith(("codeql-jdk-sources-", "codeql-jdk-sinks-")):
        combined.update(rows)

name = "codeql-servlet-sources-remote"
shutil.copyfile(work / "servlet/catalogs" / f"{name}.json", rule / "catalogs" / f"{name}.json")
catalogs.append({"path": f"catalogs/{name}.json", "semantic_hash": servlet["catalogs"][name]["semantic_hash"]})
rows = servlet["rows_by_catalog"][name]
(scope / f"{name}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
combined.update(rows)
(scope / "java-public.json").write_text(json.dumps(sorted(combined), indent=2, ensure_ascii=False) + "\n")

manifest = {
    "schema_version": 2,
    "id": "bifrost.java-codeql-security",
    "version": "0.1.0",
    "name": "Bifrost Java CodeQL security catalogs",
    "description": "Generated public Java taint source, sink, and barrier catalogs from CodeQL Models-as-Data.",
    "policies": [],
    "catalogs": catalogs,
}
(rule / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

codeql_commit = "ae741615f3e178ce61289a651790dc67fcc18e19"
engine_commit = "2eda68dc23"
jdk_input = {
    "distribution": "Eclipse Temurin",
    "runtime_version": "21+35-LTS",
    "module_image_sha256": "1465b683efd50adb60af815a8554129f8bd1b03807444cc491a5d2800d6f2091",
}
catalog_fields = (
    "catalog_version", "catalogs", "codeql_commit", "translated_rows",
    "collapsed_by_content_kind", "conflicts", "neutrals_by_kind",
    "rows_by_extensible_and_kind", "rows_by_provenance", "skipped_by_reason",
    "skipped_targets_by_reason", "source_kinds_without_threat_model",
)

def write_catalog_summary(report_path, destination, prefix, inputs):
    report = json.loads(report_path.read_text())
    summary = {
        "schema_version": 1,
        "provenance": {
            "codeql_repository": "https://github.com/github/codeql",
            "codeql_commit": codeql_commit,
            "codeql_input": "java/ql/lib/ext",
            "engine_repository": "https://github.com/BrokkAi/bifrost",
            "engine_commit": engine_commit,
            "catalog_prefix": prefix,
            "catalog_version": 1,
            "inputs": inputs,
        },
    }
    summary.update((key, report[key]) for key in catalog_fields if key in report)
    destination.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

rule_reports = rule / "generation-summaries"
if (rule / "generation-reports").exists():
    shutil.rmtree(rule / "generation-reports")
write_catalog_summary(
    work / "jdk/report.json",
    rule_reports / "jdk-generation-summary.json",
    "jdk",
    {"jdk": jdk_input},
)
write_catalog_summary(
    work / "servlet/report.json",
    rule_reports / "servlet-generation-summary.json",
    "servlet",
    {
        "jdk": jdk_input,
        "jars": [
            {"coordinate": "javax.servlet:javax.servlet-api:4.0.1", "sha256": "83a03dd877d3674576f0da7b90755c8524af099ccf0607fc61aa971535ad7c60"},
            {"coordinate": "jakarta.servlet:jakarta.servlet-api:6.0.0", "sha256": "c034eb1afb158987dbb53a5fea0cadf611c8dae8daadd59c44d9d5ab70129cef"},
        ],
    },
)

summary = json.loads((work / "summary/bifrost.java-codeql-jdk-summaries.json").read_text())
summary["pack_id"] = "bifrost.java-codeql-jdk-summaries"
summary["compatibility"]["toolchains"] = [{"name": "jdk", "requirement": ">=17.0.0"}]
for shard in summary.get("shards", []):
    for activation in shard.get("activation", []):
        if activation.get("toolchain", {}).get("name") == "jdk":
            activation["toolchain"]["version"] = ">=17.0.0"
(semantic / "bifrost.java-codeql-jdk-summaries.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
)
summary_report = json.loads((work / "summary/report.json").read_text())
summary_fields = (
    "translated_rows", "expanded_targets", "targets_with_neutral_and_flow",
    "skipped_by_reason", "collapsed_by_content_kind", "value_rows_demoted",
)
compact_report = {
    "schema_version": 1,
    "provenance": {
        "codeql_repository": "https://github.com/github/codeql",
        "codeql_commit": codeql_commit,
        "codeql_input": "java/ql/lib/ext",
        "engine_repository": "https://github.com/BrokkAi/bifrost",
        "engine_commit": engine_commit,
        "generator": "codeql-jdk-summaries",
        "jdk": jdk_input,
    },
}
compact_report.update((key, summary_report[key]) for key in summary_fields if key in summary_report)
(semantic / "generation-summary.json").write_text(
    json.dumps(compact_report, indent=2, ensure_ascii=False) + "\n"
)
(semantic / "generation-report.json").unlink(missing_ok=True)
PY
