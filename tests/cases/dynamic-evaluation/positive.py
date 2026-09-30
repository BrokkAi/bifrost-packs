"""Positive case: source text is evaluated as Python code."""

user_expression = input("expression: ")
result = eval(user_expression)
print(result)
