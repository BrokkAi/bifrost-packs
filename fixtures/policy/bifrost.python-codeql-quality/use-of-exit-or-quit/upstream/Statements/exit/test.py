# Source: github/codeql/python/ql/test/query-tests/Statements/exit/test.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

def main():
    try:
        process()
    except Exception as ex:
        print(ex)
        exit(1) # $ Alert
