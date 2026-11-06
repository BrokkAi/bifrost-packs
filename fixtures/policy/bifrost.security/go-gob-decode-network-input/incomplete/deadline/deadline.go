package deadline

import (
	"encoding/gob"
	"net"
	"time"
)

type Answer struct{ Value string }

// A direct call on the connection before the decode leaves the finding
// possible rather than definite on Bifrost 0.15.1: the run is proven by
// summary, but the finding is partial.
func fetchWithDeadline(addr string, deadline time.Time) (Answer, error) {
	var a Answer
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return a, err
	}
	defer conn.Close()
	if err := conn.SetReadDeadline(deadline); err != nil {
		return a, err
	}
	err = gob.NewDecoder(conn).Decode(&a)
	return a, err
}
