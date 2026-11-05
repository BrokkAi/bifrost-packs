package listenerclose

import (
	"encoding/gob"
	"net"
)

type Request struct{ Key string }

func handle(conn net.Conn) error {
	var req Request
	return gob.NewDecoder(conn).Decode(&req)
}

// Accepting from a listener this function opens and handing the connection to
// a helper leaves the helper's call resolution unknown on Bifrost 0.15.1, so
// the run is inconclusive. Accepting from a listener parameter is complete
// (serveWithHelper in the parent fixture), and so is decoding inline.
func listenAndServeOne(addr string) error {
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		return err
	}
	defer ln.Close()
	conn, err := ln.Accept()
	if err != nil {
		return err
	}
	defer conn.Close()
	return handle(conn)
}
