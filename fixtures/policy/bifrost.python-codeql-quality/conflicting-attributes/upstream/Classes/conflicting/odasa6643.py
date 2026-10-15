# Source: github/codeql/python/ql/test/query-tests/Classes/conflicting/odasa6643.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.
#This code has conflicting attributes,
#but the documentation in the standard library tells you do it this way :(

class ThreadingMixIn(object):

    def process_request(selfself, req):
        pass

class HTTPServer(object):

    def process_request(selfself, req):
        pass

class _ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass
