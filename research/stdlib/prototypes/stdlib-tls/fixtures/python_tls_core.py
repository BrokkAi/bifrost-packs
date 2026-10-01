"""Focused harmless TLS-state probes; these functions are not executed."""

import ssl


def insecure_active(connected_raw_client_sock, host):
    """If called, the socket argument is preconditioned as a connected client socket."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # candidate: same context disables both peer checks
    return wrapped


def secure_active(connected_raw_client_sock, host):
    context = ssl.create_default_context()
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # near miss: default chain and hostname checks remain enabled
    return wrapped


def hostname_disabled_active(connected_raw_client_sock, host):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # candidate: CERT_REQUIRED remains, hostname check is disabled
    return wrapped


def verification_disabled_but_unused():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context  # near miss: no socket wrap or handshake


def alias_mutation_active(connected_raw_client_sock, host):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    alias = context
    alias.check_hostname = False
    alias.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()  # candidate only if the same object survives the alias
    return wrapped


def verification_disabled_but_deferred(connected_raw_client_sock, host):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(
        connected_raw_client_sock, server_hostname=host, do_handshake_on_connect=False
    )
    return wrapped  # near miss within this procedure: no handshake or later use
