Probe for BrokkAi/bifrost-packs#343 on Bifrost 0.15.1 (inert; not a fixture).
Run from this directory with `BIFROST_OPEN_PACKS_DISABLE=1`,
`BIFROST_SEMANTIC_PACK_DOWNLOAD=off` and a fresh `BIFROST_CACHE_DIR`:

    bifrost --root . --query-file toolchain.rql
    bifrost --root . --query-file owner.rql

Results are in `../../README.md`.
