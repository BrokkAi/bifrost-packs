#!/usr/bin/env python3
"""Write the PHP OSV data-flow probe workspace under ../probe.

The probe is research input, not registered pack content. It declares the PHP
builtins each lead needs under the `_php_global_` type id that
`bifrost.php-builtin` uses, marks every function `callable_family_complete`,
and gives each one complete receiverless summaries. That stands in for the
bifrost-dev#9337 producer fix, which is not in the public 0.15.1 release.

Each lead gets one taint policy and a positive, a near-miss and an unknown
case. Request input comes from a workspace `request_param()` function rather
than `$_GET[...]`, so each probe measures the lead's own sink and transfer
capability apart from bifrost-dev#9330 and bifrost-dev#9331. The `superglobal`
cases measure those two issues directly.
"""

from __future__ import annotations

import json
from pathlib import Path

PROBE = Path(__file__).resolve().parents[1] / "probe"
GLOBAL_TYPE = "type.f4ebde2529e72edc1a041c3ed63b5a6284cd3d001a530fe512e521d6cbcc9c37"

# name: (stub path, [(param name, type, optional, by_ref)], transfers from these ordinals)
FUNCTIONS = {
    "file_get_contents": ("standard/standard_5.php", [("filename", "string", False), ("use_include_path", "bool", True), ("context", "mixed", True), ("offset", "int", True), ("length", "int", True)], []),
    "filter_var": ("filter/filter.php", [("value", "mixed", False), ("filter", "int", True), ("options", "mixed", True)], [0]),
    "parse_url": ("standard/standard_3.php", [("url", "string", False), ("component", "int", True)], [0]),
    "simplexml_load_string": ("SimpleXML/SimpleXML.php", [("data", "string", False), ("class_name", "string", True), ("options", "int", True), ("namespace_or_prefix", "string", True), ("is_prefix", "bool", True)], []),
    "simplexml_load_file": ("SimpleXML/SimpleXML.php", [("filename", "string", False), ("class_name", "string", True), ("options", "int", True), ("namespace_or_prefix", "string", True), ("is_prefix", "bool", True)], []),
    "proc_open": ("standard/standard_2.php", [("command", "mixed", False), ("descriptor_spec", "array", False), ("pipes", "mixed", False), ("cwd", "string", True), ("env_vars", "array", True), ("options", "array", True)], []),
    "stream_context_create": ("standard/streams.php", [("options", "array", True), ("params", "array", True)], [0]),
    "fsockopen": ("standard/standard_7.php", [("hostname", "string", False), ("port", "int", True), ("error_code", "mixed", True), ("error_message", "mixed", True), ("timeout", "float", True)], []),
    "stream_socket_client": ("standard/streams.php", [("address", "string", False)], []),
    "fread": ("standard/standard_5.php", [("stream", "mixed", False), ("length", "int", False)], [0]),
    "openssl_private_decrypt": ("openssl/openssl.php", [("data", "string", False), ("decrypted_data", "mixed", False), ("private_key", "mixed", False), ("padding", "int", True)], []),
}


def member(name: str, path: str, params) -> dict:
    """Return one callable-family-complete `_php_global_` function declaration."""
    return {
        "id": f"member.php-osv-probe.{name}",
        "owner": GLOBAL_TYPE,
        "name": name,
        "member_kind": "function",
        "visibility": "public",
        "is_static": False,
        "callable_family_complete": True,
        "aliases": [],
        "signature": {
            "parameters": [
                {"name": p, "type": {"kind": "named", "name": t}, **({"optional": True} if opt else {})}
                for p, t, opt in params
            ]
        },
        "locator": {"kind": "artifact", "path": path, "symbol": f"_php_global_.{name}"},
    }


def summaries(name: str, path: str, params, transfers) -> list[dict]:
    """Return a complete receiverless summary for every arity the function accepts."""
    required = sum(1 for _, _, opt in params if not opt)
    out = []
    for count in range(required, len(params) + 1):
        types = ", ".join(t for _, t, _ in params[:count])
        out.append({
            "id": f"php.osv-probe.{name}.{count}",
            "target": {"path": path, "symbol": f"_php_global_.{name}({types})", "has_receiver": False, "parameter_count": count},
            "completeness": "complete",
            "normal_result_count": 1,
            "transfers": [
                {"input": {"kind": "parameter", "ordinal": o}, "exit_kind": "normal", "output": {"kind": "normal_return"}}
                for o in transfers if o < count
            ],
            "effects": [],
        })
    return out


def model() -> dict:
    """Return the research semantic model that declares and summarizes every probed builtin."""
    members, sums = [], []
    for name, (path, params, transfers) in sorted(FUNCTIONS.items()):
        members.append(member(name, path, params))
        sums.extend(summaries(name, path, params, transfers))
    return {
        "schema_version": 8,
        "pack_id": "bifrost.research.php-osv-dataflow-probe",
        "version": "0.1.0",
        "producer": {"name": "bifrost-packs-research", "version": "0.1.0"},
        "language": "php",
        "ecosystem": "php",
        "compatibility": {"toolchains": []},
        "provenance": {
            "source": "https://www.php.net/manual/ function reference for " + ", ".join(sorted(FUNCTIONS)) + "; research probe, not registered pack content",
            "revision": "php-8.4",
        },
        "license": "Apache-2.0",
        "completeness": "complete",
        "safety": {"generated_code_only": False, "review_required": False},
        "shards": [
            {"id": "research.php-osv-probe.declarations", "activation": [{"targets": [], "configurations": []}],
             "payload": {"kind": "declaration_facts",
                         "types": [{"id": GLOBAL_TYPE, "name": "_php_global_", "type_kind": "module", "visibility": "public", "aliases": [],
                                    "locator": {"kind": "artifact", "path": "Core/Core.php", "symbol": "_php_global_"}}],
                         "members": members, "relations": []}},
            {"id": "research.php-osv-probe.summaries", "activation": [{"targets": [], "configurations": []}],
             "payload": {"kind": "procedure_summaries", "summaries": sums}},
        ],
    }


def call(name: str, formal: int = 0, args: str = "") -> str:
    """Return a sink selector for one formal of an exactly resolved `_php_global_` function."""
    shape = f'(call :callee (name "{name}"){args})'
    return (f'(rql :schema-version 1 (language php (call-argument :formal-index {formal} '
            f'(resolved-call :resolves-to "_php_global_.{name}" :proof declared (call-bindings (call-shape {shape}))))))')


REQUEST_SOURCE = """(source :id request-param :display-name "request parameter" :categories [input.user-controlled]
        :selector (rql :schema-version 1 (language php (call-sites-to :proof proven (enclosing-decl (function :name "request_param")))))
        :bind return-value :labels [untrusted])"""
NETWORK_SOURCE = """(source :id socket-client :display-name "stream_socket_client connection" :categories [io.external]
        :selector (rql :schema-version 1 (language php (resolved-call :resolves-to "_php_global_.stream_socket_client" :proof declared
          (call-bindings (call-shape (call :callee (name "stream_socket_client")))))))
        :bind return-value :labels [untrusted])"""


def policy(lead: str, title: str, source: str, sinks: list[tuple[str, str]]) -> str:
    """Return the research taint policy text for one lead."""
    entries = "\n      ".join(
        f'(sink :id {sid} :display-name "{sid}" :categories [x] :selector {sel} :dangerous-operand (argument :index 0) :accepts [untrusted])'
        for sid, sel in sinks
    )
    return f"""; Research probe for {lead}. Not registered pack content.
(policy
  :schema-version 1
  :id "research.php-osv.{lead}"
  :name "{title} (research probe)"
  :message "{title}"
  :severity warning
  :description "Research probe for the PHP OSV data-flow lead {lead}."
  :tags ["research" "php"]
  :analysis (analysis
    :type taint
    :mode may
    :call-modeling (call-modeling :unmodeled require-model)
    :sources (endpoint-set :entries [
      {source}])
    :sinks (endpoint-set :entries [
      {entries}])))
"""


HEAD = "<?php\n\nfunction request_param(string $name): string\n{\n    return '';\n}\n\n"
NET_HEAD = "<?php\n\n"

# lead: (title, source, sinks, {case: body})
LEADS = {
    "filter-var-url-fetch": (
        "request URL validated with FILTER_VALIDATE_URL reaches file_get_contents",
        REQUEST_SOURCE, [("file-get-contents", call("file_get_contents"))],
        {
            "positive": HEAD + "function fetch(): string|false\n{\n    $url = request_param('url');\n    if (filter_var($url, FILTER_VALIDATE_URL) === false) {\n        return false;\n    }\n    return file_get_contents($url);\n}\n",
            "positive-filtered-value": HEAD + "function fetch(): string|false\n{\n    $url = filter_var(request_param('url'), FILTER_VALIDATE_URL);\n    return file_get_contents($url);\n}\n",
            "near-miss-constant": HEAD + "function fetch(): string|false\n{\n    $url = 'https://feeds.example.test/a.xml';\n    request_param('url');\n    return file_get_contents($url);\n}\n",
            "unknown-unmodeled-trim": HEAD + "function fetch(): string|false\n{\n    $url = trim(request_param('url'));\n    return file_get_contents($url);\n}\n",
        },
    ),
    "libxml-noent-untrusted-xml": (
        "request XML parsed by simplexml_load_string with LIBXML_NOENT",
        REQUEST_SOURCE, [("simplexml-noent", call("simplexml_load_string", args=' :args [(capture "data") (capture "class") (name "LIBXML_NOENT")]'))],
        {
            "positive": HEAD + "function parse(): mixed\n{\n    return simplexml_load_string(request_param('xml'), 'SimpleXMLElement', LIBXML_NOENT);\n}\n",
            "near-miss-default-options": HEAD + "function parse(): mixed\n{\n    return simplexml_load_string(request_param('xml'));\n}\n",
            "near-miss-nonet": HEAD + "function parse(): mixed\n{\n    return simplexml_load_string(request_param('xml'), 'SimpleXMLElement', LIBXML_NONET);\n}\n",
            "unknown-flag-union": HEAD + "function parse(): mixed\n{\n    return simplexml_load_string(request_param('xml'), 'SimpleXMLElement', LIBXML_NOENT | LIBXML_DTDLOAD);\n}\n",
        },
    ),
    "proc-open-array-command": (
        "request value reaches the proc_open command",
        REQUEST_SOURCE, [("proc-open-command", call("proc_open"))],
        {
            "positive-array": HEAD + "function convert(): mixed\n{\n    $pipes = [];\n    $name = request_param('name');\n    return proc_open(['convert', $name, 'out.png'], [], $pipes);\n}\n",
            "positive-string": HEAD + "function convert(): mixed\n{\n    $pipes = [];\n    $cmd = request_param('name');\n    return proc_open($cmd, [], $pipes);\n}\n",
            "near-miss-constant": HEAD + "function convert(): mixed\n{\n    $pipes = [];\n    request_param('name');\n    return proc_open(['convert', 'in.png', 'out.png'], [], $pipes);\n}\n",
            "unknown-unmodeled-escape": HEAD + "function convert(): mixed\n{\n    $pipes = [];\n    $cmd = escapeshellarg(request_param('name'));\n    return proc_open($cmd, [], $pipes);\n}\n",
        },
    ),
    "http-context-header": (
        "request value reaches an http stream context header",
        REQUEST_SOURCE, [("stream-context-options", call("stream_context_create"))],
        {
            "positive": HEAD + "function context(): mixed\n{\n    $header = request_param('h');\n    return stream_context_create(['http' => ['header' => $header]]);\n}\n",
            "near-miss-method-only": HEAD + "function context(): mixed\n{\n    $method = request_param('m') === 'post' ? 'POST' : 'GET';\n    return stream_context_create(['http' => ['method' => 'GET']]);\n}\n",
            "near-miss-constant-header": HEAD + "function context(): mixed\n{\n    request_param('h');\n    return stream_context_create(['http' => ['header' => 'Accept: text/plain']]);\n}\n",
        },
    ),
    "http-proxy-fulluri": (
        "request URL fetched through a proxy context with request_fulluri",
        REQUEST_SOURCE, [("file-get-contents-with-context", call("file_get_contents", args=' :arity 3'))],
        {
            "positive": HEAD + "function fetch(): string|false\n{\n    $ctx = stream_context_create(['http' => ['proxy' => 'tcp://proxy.internal.test:3128', 'request_fulluri' => true]]);\n    return file_get_contents(request_param('url'), false, $ctx);\n}\n",
            "near-miss-no-proxy": HEAD + "function fetch(): string|false\n{\n    $ctx = stream_context_create(['http' => ['timeout' => 5]]);\n    return file_get_contents(request_param('url'), false, $ctx);\n}\n",
        },
    ),
    "fsockopen-host-after-check": (
        "request host reaches fsockopen after a parse_url check",
        REQUEST_SOURCE, [("fsockopen-host", call("fsockopen"))],
        {
            "positive": HEAD + "function probe(): mixed\n{\n    $url = request_param('url');\n    $host = parse_url($url, PHP_URL_HOST);\n    if ($host !== 'status.example.test') {\n        return false;\n    }\n    return fsockopen($host, 80);\n}\n",
            "near-miss-constant": HEAD + "function probe(): mixed\n{\n    request_param('url');\n    return fsockopen('status.example.test', 80);\n}\n",
            "unknown-unmodeled-strtolower": HEAD + "function probe(): mixed\n{\n    $host = strtolower(parse_url(request_param('url'), PHP_URL_HOST));\n    return fsockopen($host, 80);\n}\n",
        },
    ),
    "openssl-pkcs1-network-ciphertext": (
        "network bytes reach openssl_private_decrypt with PKCS#1 v1.5 padding",
        NETWORK_SOURCE,
        [("private-decrypt-default", call("openssl_private_decrypt", args=' :arity 3')),
         ("private-decrypt-pkcs1", call("openssl_private_decrypt", args=' :args [(capture "data") (capture "out") (capture "key") (name "OPENSSL_PKCS1_PADDING")]'))],
        {
            "positive-default-padding": NET_HEAD + "function unwrap(string $peer, mixed $key): string\n{\n    $conn = stream_socket_client($peer);\n    $bytes = fread($conn, 512);\n    $plain = '';\n    openssl_private_decrypt($bytes, $plain, $key);\n    return $plain;\n}\n",
            "positive-explicit-pkcs1": NET_HEAD + "function unwrap(string $peer, mixed $key): string\n{\n    $conn = stream_socket_client($peer);\n    $bytes = fread($conn, 512);\n    $plain = '';\n    openssl_private_decrypt($bytes, $plain, $key, OPENSSL_PKCS1_PADDING);\n    return $plain;\n}\n",
            "near-miss-oaep": NET_HEAD + "function unwrap(string $peer, mixed $key): string\n{\n    $conn = stream_socket_client($peer);\n    $bytes = fread($conn, 512);\n    $plain = '';\n    openssl_private_decrypt($bytes, $plain, $key, OPENSSL_PKCS1_OAEP_PADDING);\n    return $plain;\n}\n",
        },
    ),
    "libxml-remote-url-load": (
        "request URL loaded as XML by simplexml_load_file",
        REQUEST_SOURCE, [("simplexml-load-file", call("simplexml_load_file"))],
        {
            "positive": HEAD + "function import(): mixed\n{\n    return simplexml_load_file(request_param('feed'));\n}\n",
            "near-miss-constant": HEAD + "function import(): mixed\n{\n    request_param('feed');\n    return simplexml_load_file('/srv/app/feeds/default.xml');\n}\n",
        },
    ),
}


def main() -> None:
    """Write the model, the policies and every case file under ../probe."""
    models = PROBE / ".bifrost" / "semantic-models"
    policies = PROBE / ".bifrost" / "policies"
    models.mkdir(parents=True, exist_ok=True)
    policies.mkdir(parents=True, exist_ok=True)
    (models / "bifrost.research.php-osv-dataflow-probe.json").write_text(json.dumps(model(), indent=1) + "\n", encoding="utf-8")
    for lead, (title, source, sinks, cases) in LEADS.items():
        (policies / f"{lead}.rqlp").write_text(policy(lead, title, source, sinks), encoding="utf-8")
        for case, body in cases.items():
            target = PROBE / lead / case / "app.php"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
