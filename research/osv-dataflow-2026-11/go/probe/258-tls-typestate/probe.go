package probe

import (
	"crypto/tls"
	"crypto/x509"
	"net"
)

// Positive: the config is mutated after the listener uses it.
func reload(l net.Listener, cfg *tls.Config, pool *x509.CertPool) net.Listener {
	ln := tls.NewListener(l, cfg)
	cfg.ClientCAs = pool
	return ln
}
