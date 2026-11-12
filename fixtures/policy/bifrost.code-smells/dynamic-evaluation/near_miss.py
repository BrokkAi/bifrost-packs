"""Near misses: member calls that share a builtin's name."""

import sys

from PIL import ImageMath


def switch_to_inference(model):
    model.eval()


def derive_column(df):
    return df.eval("a + b")


def run_query(session, statement):
    return session.exec(statement)


def evaluate_image():
    return ImageMath.eval(sys.argv[1])


def pass_builtin_as_value(session, statement):
    return session.exec(statement, eval)
