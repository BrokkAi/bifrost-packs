"""Positive cases: builtin eval and exec evaluate source text as code."""

import builtins
import sys


def run_expression():
    return eval(sys.argv[1])


def run_statement():
    exec(sys.argv[2])


def run_qualified():
    return builtins.eval(sys.argv[3])
