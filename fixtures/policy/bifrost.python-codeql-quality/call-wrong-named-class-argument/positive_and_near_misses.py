def render(name, count=1):
    return name * count

# Positive: no formal named `missing`.
render(missing="x")
# Near misses: all supplied names are accepted.
render(name="x")
render(name="x", count=2)

class Widget:
    def __init__(self, name, count=1):
        self.name, self.count = name, count

# Positive constructor keyword mismatch.
Widget(missing="x")
# Accepted constructor keywords.
Widget(name="x")
Widget(name="x", count=2)
