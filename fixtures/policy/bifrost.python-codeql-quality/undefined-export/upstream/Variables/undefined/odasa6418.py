# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/odasa6418.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

import sys

def bump_version(version):
    try:
        parts = map(int, version.split('.'))
    except ValueError:
        fail('Current version is not numeric')
    parts[-1] += 1
    return '.'.join(map(str, parts))


def fail(message):
    print(message)
    sys.exit(1)

# To get the FP result reported in ODASA-6418,
#bump_version must be called (directly or transitively) from the module scope
bump_version()
