package constant

import (
	"encoding/gob"
	"net"
	"time"
)

type Answer struct{ Value string }

// time.Second has no reviewed declaration, so the procedure's semantics are
// unknown and the run is inconclusive.
func fetchFixedTimeout(addr string) (Answer, error) {
	var a Answer
	conn, err := net.DialTimeout("tcp", addr, 5*time.Second)
	if err != nil {
		return a, err
	}
	defer conn.Close()
	err = gob.NewDecoder(conn).Decode(&a)
	return a, err
}
