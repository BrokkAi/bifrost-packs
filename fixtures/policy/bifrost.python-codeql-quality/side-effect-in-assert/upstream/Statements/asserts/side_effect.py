# Source: github/codeql/python/ql/test/query-tests/Statements/asserts/side_effect.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# For now, this test lives in its own file, since including them in the top of assert.py
# messes up the results of the refers-to/points-to analysis
# see /home/rasmus/code/ql/python/ql/test/library-tests/PointsTo/regressions/subprocess-assert/mwe_failure.py
import subprocess
assert subprocess.call(['run-backup']) == 0 # $ Alert[py/side-effect-in-assert]
