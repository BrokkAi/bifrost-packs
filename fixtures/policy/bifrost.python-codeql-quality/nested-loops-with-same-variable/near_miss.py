def nested_distinct_targets(rows):
    for outer in rows:
        for inner in rows:
            consume(inner)
