def list_append(items=[]):
    items.append(1)

def dict_store(items={}):
    alias = items
    alias["key"] = 1

def delete_item(items=[1]):
    del items[0]

def augmented(items=[]):
    items += [1]

def dict_method(items={}):
    items.update({"key": 1})

def set_method(items={1}):
    items.add(2)

def dict_comprehension(items={key: key for key in ()}):
    items.update({"key": 1})

def set_comprehension(items={value for value in ()}):
    items.add(3)

def comprehension(items=[item for item in ()]):
    items.append(2)

def empty_guard(items=[]):
    if items:
        items.append(1)
    if not items:
        items.append(2)

def nonempty_guard(items=[1]):
    if items:
        items.append(2)
    if not items:
        items.append(3)

def rebound(items=[]):
    items = []
    items.append(1)

def rebound_alias(items=[]):
    alias = items
    alias = []
    alias.append(1)

def immutable(items=()):
    items += (1,)

def different_value(items=[]):
    other = []
    other.append(1)

def copy_default(items=[]):
    copied = items.copy()
    copied.append(1)
