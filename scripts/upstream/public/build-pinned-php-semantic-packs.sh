#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 OUTPUT_DIR WORK_DIR [CACHE_ROOT]" >&2
  exit 2
fi

output_dir=$1
work_dir=$2
cache_root=${3:-}
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/upstream/lib/semantic-pack-tool.sh
source "$script_directory/../lib/semantic-pack-tool.sh"
# shellcheck source=scripts/upstream/lib/semantic-pack-source.sh
source "$script_directory/../lib/semantic-pack-source.sh"
input_dir="${work_dir}/semantic-pack-inputs"
stubs_dir="${work_dir}/phpstorm-stubs"
archive_path="${input_dir}/phpstorm-stubs-748ab87d16253a5b5d648b5fe4dae1ff4152bb03.tar.gz"
archive_url="https://github.com/JetBrains/phpstorm-stubs/archive/748ab87d16253a5b5d648b5fe4dae1ff4152bb03.tar.gz"

mkdir -p "${input_dir}" "${stubs_dir}"
fetch_pinned_archive \
  "${archive_path}" \
  "${archive_url}" \
  "b83242b6471ca748de192c1d1df73ebcd565aee48d9e41e467cf99db78d2e4bd" \
  "phpstorm-stubs-748ab87d16253a5b5d648b5fe4dae1ff4152bb03.tar.gz"
tar -C "${stubs_dir}" -xzf "${archive_path}"
# The pinned artifact is a source set, not one file. Its canonical digest
# covers the stub paths and bytes the specification lists, so `generate`
# verifies the extracted tree itself. The directory name is pinned too, so
# copy the stub root to the name the specification records. Copying the
# contents keeps a repeated run in the same work directory idempotent instead
# of nesting a second stub root below the pinned artifact root. The whole
# archive top directory is the stub root; unlike typeshed there is no inner
# subdirectory to descend into.
mkdir -p "${input_dir}/phpstorm-stubs-748ab87d1625"
cp -R \
  "${stubs_dir}/phpstorm-stubs-748ab87d16253a5b5d648b5fe4dae1ff4152bb03/." \
  "${input_dir}/phpstorm-stubs-748ab87d1625/"

run_semantic_pack_tool generate \
  "${output_dir}" \
  semantic-packs/php/phpstorm-stubs-2026.8.29.json \
  "${input_dir}/phpstorm-stubs-748ab87d1625"
run_semantic_pack_tool verify "${output_dir}"

if [[ -n "${cache_root}" ]]; then
  catalog_version=$(sed -nE \
    's/^pub\(super\) const CURRENT_CATALOG_VERSION: i64 = ([0-9]+);$/\1/p' \
    crates/bifrost-analysis/src/analyzer/semantic_model/catalog/db.rs)
  if [[ ! "${catalog_version}" =~ ^[0-9]+$ ]]; then
    echo "could not derive exactly one numeric semantic-pack catalog version" >&2
    exit 2
  fi
  catalog_directory="semantic-pack-catalog.v${catalog_version}"
  mkdir -p "${cache_root}"
  run_semantic_pack_tool install \
    "${output_dir}" "${cache_root}/${catalog_directory}"
fi
