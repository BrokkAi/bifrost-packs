def run(task):
    try:
        task()
    except:
        pass


def parse(text):
    try:
        return int(text)
    except ValueError:
        pass
    return None


def interrupt(task):
    try:
        task()
    except KeyboardInterrupt:
        pass


def unfinished(task):
    try:
        task()
    except OSError:
        # TODO: report this to the caller
        pass


def first(items):
    try:
        return next(iter(items))
    except StopIteration:
        ...


def broad(task):
    try:
        task()
    except (ImportError, OSError) as error:
        print(error)
    except Exception:
        pass


try:
    import optional_dependency
except ImportError:
    # TODO: report the missing dependency
    pass


try:
    import optional_dependency
except (ImportError, Exception):
    pass
