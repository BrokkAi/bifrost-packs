# Rust non-HTTPS URL literals

CodeQL query: rust/ql/src/queries/security/CWE-319/UseOfHttp.ql
CodeQL commit: ae741615f3e178ce61289a651790dc67fcc18e19
Engine source revision: 26c360ce219bab07f6224a490468741151b64623

The fixture uses the stable policy ID bifrost.security.rust.non-https-url. It expects five external HTTP literals and excludes HTTPS, localhost, loopback, and private-network authorities. Literals inside a standard formatting macro call whose authority begins with an unescaped format placeholder, such as `format!("http://{}", listener.local_addr()?)`, are near-misses: the host is supplied at run time, so the literal names no external authority (bifrost-packs#339). A literal host before the placeholders, an escaped `{{`, and a `"http://{}"` literal outside a formatting macro remain findings. The policy matches decoded literal values and does not claim to cover request-construction flows, which belong to the separate request-forgery rule.
