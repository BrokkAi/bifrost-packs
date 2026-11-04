import os as operating_system
from os import chmod as chmod_alias
from os import open as open_alias


def configure(path):
    operating_system.chmod(path, 0o777)
    chmod_alias(path, 0o600)
    operating_system.open(path, operating_system.O_CREAT, 0o644)
    open_alias(path, 0, mode=0o600)
    operating_system.chmod(path, 0o700)


def chmod(path, mode):
    return None


def local_lookalike(path):
    return chmod(path, 0o777)
