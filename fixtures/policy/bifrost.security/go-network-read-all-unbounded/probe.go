// Fixture for bifrost.security.go.network-read-all-unbounded (lead #252).
package probe

import (
	"compress/gzip"
	"io"
	"net"
	"os"
	"time"
)

// Positive: a dialed peer controls a gzip stream that is inflated without a bound.
func fetchCompressed(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return nil, err
	}
	defer zr.Close()
	return io.ReadAll(zr)
}

// Positive: the server side, inflating what a client sends.
func receiveCompressed(ln net.Listener) ([]byte, error) {
	conn, err := ln.Accept()
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(zr)
}

// Positive: an uncompressed connection read to EOF has no bound either.
func fetchRaw(addr string, timeout time.Duration) ([]byte, error) {
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	return io.ReadAll(conn)
}

// Positive: the accepted connection is inflated by a helper.
func receiveWithHelper(ln net.Listener) ([]byte, error) {
	conn, err := ln.Accept()
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	return inflate(conn)
}

func inflate(r io.Reader) ([]byte, error) {
	zr, err := gzip.NewReader(r)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(zr)
}

// Near miss: the decompressed size is bounded.
func fetchCompressedLimited(addr string) ([]byte, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}
	defer conn.Close()
	zr, err := gzip.NewReader(conn)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(io.LimitReader(zr, 1048576))
}

// Near miss: a local file the program controls, not a peer.
func readLocal(path string) ([]byte, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	zr, err := gzip.NewReader(f)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(zr)
}
