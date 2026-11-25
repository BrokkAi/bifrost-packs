package exchange

import (
	"encoding/gob"
	"net"
)

type Query struct{ Key string }

type Answer struct{ Value string }

// Encoding on the connection before decoding from it leaves the procedure's
// call resolution unknown on Bifrost 0.15.1, so the run is inconclusive.
func exchange(addr string, q Query) (Answer, error) {
	var a Answer
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return a, err
	}
	defer conn.Close()
	if err := gob.NewEncoder(conn).Encode(q); err != nil {
		return a, err
	}
	err = gob.NewDecoder(conn).Decode(&a)
	return a, err
}
