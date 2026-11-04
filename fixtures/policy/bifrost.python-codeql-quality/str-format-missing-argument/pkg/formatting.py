two_fields = "{0}, {1}"
one_field = "{0}"

bad = two_fields.format("one")
good = two_fields.format("one", "two")
near_miss = one_field.format("one")
