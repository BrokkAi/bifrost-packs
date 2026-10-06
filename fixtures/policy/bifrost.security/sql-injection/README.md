# Rust SQL injection

CodeQL query: `rust/ql/src/queries/security/CWE-089/SqlInjection.ql`
CodeQL commit: `ae741615f3e178ce61289a651790dc67fcc18e19`
Engine source revision: `26c360ce219bab07f6224a490468741151b64623`

The public policy uses stable ID `bifrost.security.rust.sql-injection`. Its sources cover `std::env::var`, `std::env::args().nth`, and `Stdin::read_line`. Its sinks cover SQL text in `postgres::Client::execute` and `rusqlite::Connection::execute`. The three Apache-2.0 Bifrost-authored semantic models provide the reviewed standard-library input and database API semantics.

The standard-input fixtures independently exercise all three input forms through each database driver. Each also includes a same-shaped query that uses parameter binding and a separate query that does not receive the input; neither near miss should produce a finding. Model-backed results may conclude `proven_by_summary`, preserving the reviewed summary provenance.

The import is limited to the tested standard-library input APIs and PostgreSQL/rusqlite methods under `semantic-packs/rust-sql-injection`. SQLx, tokio-postgres, MySQL, Diesel, database-row sources, and web-framework request models are excluded because they were outside these accepted fixture runs; premium framework models are not included.
