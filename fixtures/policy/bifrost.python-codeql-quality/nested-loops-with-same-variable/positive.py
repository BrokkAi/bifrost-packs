def nested_same_target(rows):
    for item in rows:
        print(item)
        for item in rows:
            consume(item)
