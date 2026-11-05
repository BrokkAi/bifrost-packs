package copied

import (
	"bytes"
	"compress/gzip"
	"io"
	"net"
)

// io.Copy writes into its destination, which the summary schema cannot
// express, so it has no reviewed model and the run stays inconclusive.
func fetchInto(addr string, buf *bytes.Buffer) error {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return err
	}
	defer conn.Close()
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return err
	}
	_, err = io.Copy(buf, zr)
	return err
}
