import imaplib


def connect(host):
    return imaplib.IMAP4_SSL(host)
