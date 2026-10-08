import ssl


def exercise(sock):
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv2)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv3)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_1)
    ssl.SSLContext(ssl.PROTOCOL_SSLv2)
    ssl.SSLContext(ssl.PROTOCOL_SSLv3)
    ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    ssl.SSLContext(ssl.PROTOCOL_TLSv1_1)
    ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)
    ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS_CLIENT)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS_SERVER)
    ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
    wrap_socket(sock, ssl.PROTOCOL_SSLv3)


def wrap_socket(sock, protocol):
    return sock
