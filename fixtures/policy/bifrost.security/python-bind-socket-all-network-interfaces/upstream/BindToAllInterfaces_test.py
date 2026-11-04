# Source: github/codeql/python/ql/test/query-tests/Security/CVE-2018-1281/BindToAllInterfaces_test.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
import socket


def upstream_examples():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 31137))
    sock.bind(('', 4040))
    sock.bind(('84.68.10.12', 8080))
    sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock6.bind(('::', 8080))
    local = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    local.bind('service.sock')
