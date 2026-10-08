import socket


def bind_ipv4():
    sock = socket.socket()
    endpoint = ("0.0.0.0", 8080)
    sock.bind(endpoint)


def bind_ipv6():
    sock = socket.socket()
    host = "::"
    sock.bind((host, 8080))


def bind_empty():
    sock = socket.socket()
    sock.bind(("", 8080))


class LocalSocket:
    def bind(self, address):
        return address


def bind_loopback():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 8080))


def bind_unix():
    sock = socket.socket()
    sock.bind("service.sock")


def bind_unrelated():
    LocalSocket().bind(("0.0.0.0", 8080))
