import imaplib
import sys


def run():
    command = sys.argv[1]
    imap = imaplib.IMAP4("mail.example.invalid")
    return imap.xatom(command)
