#!/usr/bin/env bash

# Run the pinned released producer. There is deliberately no fallback to
# `cargo run`: from a Bifrost checkout that would silently build an
# unreleased engine. Download the producer named in native-generation.json
# and point BIFROST_SEMANTIC_PACK_BIN at it.
run_semantic_pack_tool() {
  if [[ -z "${BIFROST_SEMANTIC_PACK_BIN:-}" ]]; then
    echo "BIFROST_SEMANTIC_PACK_BIN must name the released bifrost-semantic-pack pinned in native-generation.json" >&2
    exit 2
  fi
  [[ -x "${BIFROST_SEMANTIC_PACK_BIN}" ]] || {
    echo "BIFROST_SEMANTIC_PACK_BIN must name an executable file" >&2
    exit 2
  }
  "${BIFROST_SEMANTIC_PACK_BIN}" "$@"
}
