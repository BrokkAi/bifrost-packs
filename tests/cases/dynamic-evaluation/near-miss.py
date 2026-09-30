"""Near miss: parse data using Python's literal-only parser."""

import ast

user_value = input("literal value: ")
result = ast.literal_eval(user_value)
print(result)
