package main

import (
	"encoding/gob"
	"net"
)

type Msg struct{ A string }

// A peer reached with net.Dial controls every byte the decoder reads.
func fetch(addr string) (Msg, error) {
	var m Msg
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return m, err
	}
	err = gob.NewDecoder(conn).Decode(&m)
	return m, err
}
