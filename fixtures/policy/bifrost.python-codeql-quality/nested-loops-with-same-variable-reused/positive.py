def reused_target(rows):
    for item in rows:
        for item in rows:
            consume(item)
        consume(item)
