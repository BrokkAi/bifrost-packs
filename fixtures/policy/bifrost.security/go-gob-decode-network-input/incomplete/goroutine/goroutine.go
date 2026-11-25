package goroutine

import (
	"encoding/gob"
	"net"
)

type Request struct{ Key string }

func handleConn(conn net.Conn) error {
	defer conn.Close()
	var req Request
	return gob.NewDecoder(conn).Decode(&req)
}

// The usual accept loop. A handler started with `go` leaves its value-flow
// snapshot unknown on Bifrost 0.15.1, so the run is inconclusive.
func serve(ln net.Listener) error {
	for {
		conn, err := ln.Accept()
		if err != nil {
			return err
		}
		go handleConn(conn)
	}
}
