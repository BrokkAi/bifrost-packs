package probe

import (
	"compress/gzip"
	"io"
	"net"
)

// Positive: a dialed peer controls the compressed stream, drained without a bound.
func fetch(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(zr)
}

// Near miss: the decompressed size is bounded.
func fetchLimited(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(io.LimitReader(zr, 1048576))
}

// Near miss: raw connection bytes, no decompression.
func fetchRaw(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(io.LimitReader(conn, 4096))
}
