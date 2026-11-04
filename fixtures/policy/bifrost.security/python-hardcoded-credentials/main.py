import ftplib
import hmac
import smtplib


def direct_hmac_credentials():
    hmac.new(b"hardcoded-hmac-key-value", b"payload", digestmod="sha256")
    hmac.new(b"short", b"long-message-is-not-the-key", digestmod="sha256")


def direct_mail_credentials():
    smtp = smtplib.SMTP()
    smtp.login("user", "smtp-hardcoded-secret")
    smtp.login("user", "short")
    ftp = ftplib.FTP()
    ftp.login("user", "ftp-hardcoded-secret")
    ftplib.FTP(passwd="ftp-constructor-secret")
