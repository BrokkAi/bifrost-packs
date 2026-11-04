# Source: github/codeql/python/ql/test/query-tests/Security/CWE-327-InsecureDefaultProtocol/InsecureProtocol.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
# The upstream call omits required parameter `sock`; this uses the same default
# protocol case with a valid stdlib call signature.
import ssl


def upstream_default_protocol(sock):
    ssl.wrap_socket(sock)


def upstream_explicit_modern_protocol(sock):
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
