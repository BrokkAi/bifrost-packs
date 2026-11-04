def render(name, count=1):
    return name * count

# Positive: no formal named `missing`.
render(missing="x")
# Near misses: all supplied names are accepted.
render(name="x")
render(name="x", count=2)
