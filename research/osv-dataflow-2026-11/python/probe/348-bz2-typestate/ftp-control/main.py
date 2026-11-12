"""Research probe for BrokkAi/bifrost-packs#348: the `ftp-control` case."""
import ftplib

failures = []


def f(host, user, password):
    """Exercise the f case."""
    ftp = ftplib.FTP(host)
    try:
        ftp.login(user, password)
    except OSError as error:
        failures.append(error)
    return ftp.login(user, password)
