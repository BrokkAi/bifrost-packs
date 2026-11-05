package goroutine

import (
	"compress/gzip"
	"io"
	"net"
)

// The usual accept loop: the handler runs in its own goroutine.
func serve(ln net.Listener) error {
	for {
		conn, err := ln.Accept()
		if err != nil {
			return err
		}
		go handle(conn)
	}
}

func handle(conn net.Conn) {
	defer conn.Close()
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return
	}
	_, _ = io.ReadAll(zr)
}
