def no_reuse_after_inner(rows):
    for item in rows:
        for item in rows:
            consume(item)
