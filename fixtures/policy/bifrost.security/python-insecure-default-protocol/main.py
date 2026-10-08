import ssl


def unsafe(sock):
    return ssl.wrap_socket(sock)


def explicit_safe_version(sock):
    return ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
