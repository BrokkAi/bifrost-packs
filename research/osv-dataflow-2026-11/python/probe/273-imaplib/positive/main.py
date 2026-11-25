import imaplib
import sys


def run():
    imap = imaplib.IMAP4("mail.example.invalid")
    return imap.xatom(sys.argv[1])
