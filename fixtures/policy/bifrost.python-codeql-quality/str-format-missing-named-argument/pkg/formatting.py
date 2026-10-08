named = "{name}"
bad = named.format("value")
good = named.format(name="value")
near_miss = "{0}".format("value")
