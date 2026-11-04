# Source: github/codeql/python/ql/test/query-tests/Security/CWE-020-IncompleteUrlSubstringSanitization/urltest.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
# Flask request/redirect wrappers were omitted; the checks below are the stdlib-free
# structural cases selected by the public rule.
from urllib.parse import urlparse


def upstream_url_checks(target):
    if "example.com" in target:
        pass
    if target.endswith("example.com"):
        pass
    allowlist = ["example.com/home", "example.com/login"]
    if target in allowlist:
        pass
    host = urlparse(target).hostname
    if host and host.endswith(".example.com"):
        pass
    parsed = urlparse(target)
    if parsed and parsed.startswith("https://example.com/"):
        pass
