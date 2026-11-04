# Rust non-HTTPS URL literals

CodeQL query: rust/ql/src/queries/security/CWE-319/UseOfHttp.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Engine source revision: 26c360ce219bab07f6224a490468741151b64623

The fixture uses the stable policy ID bifrost.security.rust.non-https-url. It expects the two external HTTP literals and excludes HTTPS, localhost, loopback, and private-network authorities. The policy matches decoded literal values and does not claim to cover request-construction flows, which belong to the separate request-forgery rule.
