import imaplib
import sys


def run():
    imap = imaplib.IMAP4("mail.example.invalid")
    label = sys.argv[1]
    return imap.xatom("ID"), label
