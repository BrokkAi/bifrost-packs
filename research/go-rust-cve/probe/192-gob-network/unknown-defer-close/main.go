package main

import (
	"encoding/gob"
	"net"
)

type Msg struct{ A string }

// Same flow as positive-dial, plus the usual deferred Close on the net.Conn.
func fetch(addr string) (Msg, error) {
	var m Msg
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return m, err
	}
	defer conn.Close()
	err = gob.NewDecoder(conn).Decode(&m)
	return m, err
}
