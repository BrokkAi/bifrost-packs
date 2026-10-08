# Source: github/codeql/python/ql/test/query-tests/Security/CWE-020-IncompleteHostnameRegExp/hosttest.py @ ae741615f3e178ce61289a651790dc67fcc18e19; MIT License, Copyright GitHub, Inc.
import re

UNSAFE_REGEX = re.compile("(www|beta).example.com/")
SAFE_REGEX = re.compile(r"(www|beta)\.example\.com/")
escaped = re.escape("https://www.humblebundle.com/home/library")
