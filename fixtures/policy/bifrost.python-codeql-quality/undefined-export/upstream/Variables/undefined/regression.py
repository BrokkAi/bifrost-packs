# Source: github/codeql/python/ql/test/query-tests/Variables/undefined/regression.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
# Regression test for a false-positive in 'Uninitialized Local'

def func():
    safe = 0
    for i in []:
        safe = 1
        if True:
            pass
    print safe # wrongly flagged

from module1 import *

def func2():
    os

def findPluginJars(dir):
  return filter(lambda y: y,
     (os.path.join(root, f) for root, _, files in os.walk(dir + '/plugins') for f in files))
