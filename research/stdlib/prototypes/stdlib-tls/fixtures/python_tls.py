"""Harmless, source-only SSLContext typestate probes; none of these run here."""

import ssl


def insecure_same_context(connected_raw_client_sock, host):
    """`connected_raw_client_sock` is preconditioned as a connected client socket."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # expected positive: same context disables chain and hostname checks
    return wrapped


def secure_default_same_context(connected_raw_client_sock, host):
    context = ssl.create_default_context()
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # expected near miss: verified peer and hostname
    return wrapped


def hostname_only_missing(connected_raw_client_sock, host):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # expected positive only for hostname verification
    return wrapped  # CERT_REQUIRED still validates the certificate chain


def disabled_but_unused():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context  # expected near miss: no wrap or handshake


def alias_mutation_reaches_wrap(raw_sock, host):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    alias = context
    alias.check_hostname = False
    alias.verify_mode = ssl.CERT_NONE
    return context.wrap_socket(raw_sock)  # expected positive if alias identity is retained


def secure_but_handshake_deferred(connected_raw_client_sock, host):
    context = ssl.create_default_context()
    wrapped = context.wrap_socket(
        connected_raw_client_sock, server_hostname=host, do_handshake_on_connect=False
    )
    return wrapped  # expected near miss: no do_handshake or later use in this procedure


class SSLContext:
    """Local lookalike: same spelling, unrelated API identity."""

    def __init__(self, protocol):
        self.protocol = protocol

    def wrap_socket(self, raw_sock, **kwargs):
        return raw_sock


def local_same_name_type(raw_sock):
    context = SSLContext(0)
    context.verify_mode = 0
    return context.wrap_socket(raw_sock)  # expected near miss: local type, no TLS contract
