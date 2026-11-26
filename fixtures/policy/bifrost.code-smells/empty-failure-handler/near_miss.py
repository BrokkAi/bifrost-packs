try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib
except ModuleNotFoundError:
    pass

try:
    from _distutils_hack import remove_shim
except (ImportError, AttributeError):
    pass


def remove(path, os):
    try:
        os.remove(path)
    except FileNotFoundError:
        # Already gone, which is what we wanted.
        pass


def size(os, fd):
    try:
        return os.get_terminal_size(fd)
    except OSError:  # not a terminal
        pass


def close(handle):
    try:
        handle.close()
    except OSError as ignored:
        pass
