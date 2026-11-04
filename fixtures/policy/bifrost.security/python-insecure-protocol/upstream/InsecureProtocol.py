# Source: github/codeql/python/ql/test/query-tests/Security/CWE-327-InsecureProtocol/InsecureProtocol.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
# Calls include the required socket argument so the stdlib signatures are valid.
import ssl


def upstream_explicit_protocols(sock):
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv2)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv3)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1)
    ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv2)
    ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv3)
    ssl.SSLContext(protocol=ssl.PROTOCOL_TLSv1)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
    ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
