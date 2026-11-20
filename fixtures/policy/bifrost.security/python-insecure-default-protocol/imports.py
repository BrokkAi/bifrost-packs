"""Import forms of ssl.wrap_socket: two the policy selects and one renamed import it does not."""

import ssl as tls
from ssl import wrap_socket
from ssl import wrap_socket as renamed_wrap_socket


def imported_default(sock):
    return wrap_socket(sock)


def module_alias_default(sock):
    return tls.wrap_socket(sock)


def renamed_import_default(sock):
    return renamed_wrap_socket(sock)
