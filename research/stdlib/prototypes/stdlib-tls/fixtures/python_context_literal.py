"""Isolation control: state operations on an injected context with scalar inputs."""


def context_properties_with_scalar_mode(context, connected_raw_client_sock, host):
    context.check_hostname = False
    context.verify_mode = 0
    wrapped = context.wrap_socket(connected_raw_client_sock, server_hostname=host)
    wrapped.do_handshake()
    return wrapped
