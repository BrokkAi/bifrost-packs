package wrapped

import (
	"bufio"
	"encoding/gob"
	"net"
)

type Reply struct{ Value string }

// bufio.NewReader has no reviewed summary, so the flow through it is not
// established and the run stays inconclusive.
func fetchBuffered(addr string) (Reply, error) {
	var r Reply
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return r, err
	}
	defer conn.Close()
	err = gob.NewDecoder(bufio.NewReader(conn)).Decode(&r)
	return r, err
}
