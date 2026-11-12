package wrapped

import (
	"bufio"
	"compress/gzip"
	"io"
	"net"
)

// bufio.NewReader has no reviewed summary, so the flow through it is not
// established and the run stays inconclusive.
func fetchBuffered(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	zr, err := gzip.NewReader(bufio.NewReader(conn))
	if err != nil {
		return nil, err
	}
	return io.ReadAll(zr)
}
