"""Diagnostic isolation: same context property operations with ssl.CERT_NONE."""

import ssl


def context_properties_with_stdlib_mode(context, connected_raw_client_sock, host):
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()
    return wrapped
