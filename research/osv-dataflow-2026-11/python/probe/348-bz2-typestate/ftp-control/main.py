import ftplib


def f(host, user, password):
    ftp = ftplib.FTP(host)
    try:
        ftp.login(user, password)
    except OSError:
        pass
    return ftp.login(user, password)
