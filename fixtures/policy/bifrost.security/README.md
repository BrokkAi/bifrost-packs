# Public C# and Rust CodeQL security fixtures

The C# fixtures exercise the five public BCL-backed injection policies. The Rust fixture covers the non-HTTPS URL literal rule, which classifies string values structurally and requires no third-party semantic models.

`signedxml-embedded-key-trust` is not a CodeQL port. It qualifies the
version-independent part of the .NET CVE lead BrokkAi/bifrost-packs#154 against
the reviewed `bifrost.dotnet.security-cryptography-xml-csharp` model.

`xmldocument-url-resolver` is not a CodeQL port either. It qualifies the
XmlDocument part of the stdlib candidate
`dotnet-xmlreader-external-dtd-resolution` against the reviewed
`bifrost.dotnet.system-xml-csharp` model.

`regex-pattern-injection` and `dataset-read-xml-external-location` are not
CodeQL ports. They qualify the version-independent parts of the .NET CVE leads
BrokkAi/bifrost-packs#263 (CVE-2019-0820) and #262 (CVE-2020-1147) against the
reviewed `bifrost.dotnet.system-text-regularexpressions-csharp` and
`bifrost.dotnet.system-data-csharp` models.

`go-gob-decode-network-input` is not a CodeQL port. It qualifies the
version-independent part of the Go CVE lead BrokkAi/bifrost-packs#192 against
the reviewed `bifrost.go.stdlib.net` and `bifrost.go.stdlib.encoding-gob`
models.

`go-network-read-all-unbounded` is not a CodeQL port either. It qualifies the
version-independent part of the Go CVE lead BrokkAi/bifrost-packs#252 against
the reviewed `bifrost.go.stdlib.net`, `bifrost.go.stdlib.compress-gzip` and
`bifrost.go.stdlib.io` models.

`java-objectinputstream-read-without-filter` is not a CodeQL port. It
qualifies the version-independent part of the Java CVE lead
BrokkAi/bifrost-packs#301 (CVE-2026-41586) against the generated JDK members
for `java.io.ObjectInputStream`. On Bifrost 0.15.1 every run is inconclusive
and every finding is `possible`; see its `README.md`.

`python-http-client-tls-verification` is not a CodeQL port. It qualifies the
version-independent part of the Python HTTP-client lead BrokkAi/bifrost-packs#427
(CWE-295): four opt-in rules, one each for requests, httpx, aiohttp and urllib3,
against the reviewed declarations in `semantic-packs/python/http-client/`.

The Rust SAST fixtures cover unsafe marker impl bounds and caller-supplied calls after invalid-state APIs. Their isolated positive and near-miss crates are fresh public sources. See each `expectations.json` and `scripts/rust-sast-gate.py`. All 37 cases pass on public Bifrost 0.15.0; see `docs/qualification/rust-sast.json`.

`cargo-ssh-git-host-key-unverified` qualifies the Rust CVE lead
BrokkAi/bifrost-packs#60 (CVE-2022-46176). It needs Bifrost 0.15.3, which
accepts its empty `required_capabilities` list, Cargo and `rust-toolchain`
dependency evidence and TOML configuration facts, and no semantic models. Its
16 cases include four where the toolchain or lockfile is unknown, and those
must stay inconclusive. See its `README.md` and
`docs/qualification/rust-cargo-ssh-git.json`.

`python-process-input-to-urlopen` and `python-process-input-to-webbrowser-open`
are not CodeQL ports. They qualify the version-independent parts of the Python
CVE leads BrokkAi/bifrost-packs#270 and #272 against the reviewed
`bifrost.python-process-inputs`, `bifrost.python-stdlib-api-declarations` and
`bifrost.python-security-sink-summaries` models.

`python-process-input-to-venv-create` is not a CodeQL port either. It
qualifies the version-independent part of the Python CVE lead
BrokkAi/bifrost-packs#355 (CVE-2024-9287) against the same reviewed models,
which now declare and summarize `venv.create`.

`csharp-webassembly-debugging-affected-version` is not a CodeQL port. It
qualifies the affected-version part of the .NET CVE lead
BrokkAi/bifrost-packs#167 (CVE-2026-96230) against the new
`bifrost.dotnet.aspnetcore-webassembly-server-csharp` and
`bifrost.dotnet.aspnetcore-hosting-csharp` models. The version gate comes from
restored NuGet evidence.

`ruby-network-xml-to-rexml`, `ruby-network-input-to-net-imap` and
`ruby-network-input-to-gem-installer` qualify the Ruby CVE leads
BrokkAi/bifrost-packs#363 and #364 (rexml), #368 and #369 (net-imap), and the
version-independent install part of #286 (RubyGems) against the new
`bifrost.ruby.rexml`, `bifrost.ruby.net-imap` and
`bifrost.ruby.rubygems-installer` models and the reviewed
`bifrost.web-network-ruby` source. The rexml and net-imap gates come from
Gemfile.lock. All of these cases run on Bifrost 0.15.2.

`javascript-process-input-to-fs-path`,
`javascript-process-input-to-child-process-command` and
`javascript-process-input-to-vm-code` qualify the path-traversal,
command-injection and code-injection parts of the Node core lead
BrokkAi/bifrost-packs#393 on Bifrost 0.15.3. Each has a positive and near-miss
workspace and an `incomplete/` workspace that must stay inconclusive. The
command fixture also has an `uncovered/` workspace for `execFile` with an
argument array, which runs no shell and is not a sink. See each `README.md`.

`javascript-file-content-to-unbounded-decompression` qualifies the
version-independent part of BrokkAi/bifrost-packs#291 (CVE-2024-22025) on
Bifrost 0.15.4: an `fs.readFileSync` buffer that reaches a `zlib`
convenience method called without options, which has no `maxOutputLength`
limit. It needs the new source-only `bifrost.node-zlib-javascript-*` packs.
It has `incomplete/` and `uncovered/` workspaces. See its `README.md`.

`javascript-process-input-to-fetch-url` qualifies the global `fetch` part of
BrokkAi/bifrost-packs#478 (CVE-2025-27152) on Bifrost 0.15.4: a
`process.argv` value that reaches the URL of `fetch(input)` or
`fetch(input, init)`. The one-argument form needs
`bifrost.web-network-javascript` 1.1.0. It has `incomplete/` and `inline/`
workspaces. See its `README.md`.

`php-request-input-to-proc-open-command` qualifies the version- and
OS-independent part of BrokkAi/bifrost-packs#311 (CVE-2024-1874). It needs a
`bifrost.php-builtin` pack generated by `bifrost-semantic-pack` 0.15.2 or
later and the reviewed `bifrost.php-process-summaries`. See its `README.md`.

`ruby-network-input-to-net-imap-host` qualifies BrokkAi/bifrost-packs#284
(CVE-2026-42245): a `Net::HTTP.get` body that chooses the server of
`Net::IMAP.new` on an affected net-imap. It needs Bifrost 0.15.3, which binds
keyword arguments to model members, and `bifrost.ruby.net-imap` 0.2.0. See its
`README.md`.

`python-flask-request-sources` and `python-django-request-sources` are for the
opt-in Flask and Django request-to-`urlopen` policies of bifrost-dev#14549.
They need the source-only packs in `semantic-packs/python/web-request/`, which
activate from lockfile or pinned-requirement `pkg:pypi` evidence on Bifrost 0.15.4
or later (bifrost-dev#14581). The stdlib `urlopen` sink also needs the open packs.
See each `README.md` for the results on the 0.15.4 release.
