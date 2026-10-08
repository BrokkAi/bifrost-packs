# Source: github/codeql/python/ql/test/query-tests/Security/CWE-732-WeakFilePermissions/test.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
import os


def upstream_modes(path):
    os.chmod(path, 0o7)
    os.chmod(path, 0o77)
    os.chmod(path, 0o777)
    os.chmod(path, 0o600)
    os.chmod(path, 0o550)
    os.chmod(path, 400)
    os.open(path, os.O_CREAT, 0o704)
