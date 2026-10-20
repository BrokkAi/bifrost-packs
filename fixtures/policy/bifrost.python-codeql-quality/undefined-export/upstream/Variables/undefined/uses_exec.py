# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/uses_exec.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
from other import setup

exec('x/_version.py')

setup(
    name='x',
    version=__version__
    )
