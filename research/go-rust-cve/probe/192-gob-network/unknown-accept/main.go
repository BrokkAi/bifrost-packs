package main

import (
	"encoding/gob"
	"net"
)

type Msg struct{ A string }

// The server-side case from the advisory: decode what a client sends.
func serve(ln net.Listener) (Msg, error) {
	var m Msg
	conn, err := ln.Accept()
	if err != nil {
		return m, err
	}
	err = gob.NewDecoder(conn).Decode(&m)
	return m, err
}
