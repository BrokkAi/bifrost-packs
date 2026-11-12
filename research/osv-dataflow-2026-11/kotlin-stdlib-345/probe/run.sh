#!/bin/sh
# Rechecks bifrost-packs#345 on released Bifrost v0.15.1. Needs
# kotlin-stdlib 2.2.20 (jar and -sources.jar) in ~/.m2 and, for the
# bifrost.kotlin-stdlib decision, the packs/v0.11.0 native bundle.
set -eu
: "${BIFROST_BIN:?set BIFROST_BIN to the v0.15.1 bifrost binary}"
here=$(cd "$(dirname "$0")" && pwd)
export BIFROST_SEMANTIC_PACK_DOWNLOAD=off BIFROST_WORKSPACE_SEMANTIC_MODELS=on
[ -n "${BIFROST_OPEN_SEMANTIC_PACK_BUNDLE:-}" ] || export BIFROST_OPEN_PACKS_DISABLE=1
for q in create-temp-dir create-temp-file; do
  work=$(mktemp -d); cp -R "$here/root/." "$work/"; cp "$here/queries/$q.rql" "$work/q.rql"
  echo "== $q"
  (cd "$work" && BIFROST_CACHE_DIR=$(mktemp -d) "$BIFROST_BIN" --root . --query-file q.rql) |
    jq -c '.structuredContent.results[] | {line: .range.start_line, dispatch_outcome, dispatch_coverage, dispatch_target_count, reason}'
done
