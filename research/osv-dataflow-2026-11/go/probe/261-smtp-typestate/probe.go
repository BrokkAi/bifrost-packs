package probe

import (
	"crypto/tls"
	"net/smtp"
)

// Positive: PLAIN credentials on a cleartext session.
func sendCleartext(user, pass string) error {
	c, err := smtp.Dial("mail.example.com:25")
	if err != nil {
		return err
	}
	return c.Auth(smtp.PlainAuth("", user, pass, "mail.example.com"))
}

// Near miss: STARTTLS first.
func sendTLS(user, pass string, cfg *tls.Config) error {
	c, err := smtp.Dial("mail.example.com:25")
	if err != nil {
		return err
	}
	if err := c.StartTLS(cfg); err != nil {
		return err
	}
	return c.Auth(smtp.PlainAuth("", user, pass, "mail.example.com"))
}
