# Source: github/codeql/python/ql/src/Classes/InconsistentMRO.py at ae741615
# MIT License, Copyright GitHub, Inc.
class X(object):
    def __init__(self):
        print("X")
class Y(object,X):
    def __init__(self):
        print("Y")