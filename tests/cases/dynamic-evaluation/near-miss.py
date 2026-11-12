"""Near miss: literal-only parsing and member calls that share a builtin's name."""

import ast


def switch_to_inference(model):
    model.eval()


def run_query(session, statement):
    return session.exec(statement)


user_value = input("literal value: ")
result = ast.literal_eval(user_value)
print(result)
