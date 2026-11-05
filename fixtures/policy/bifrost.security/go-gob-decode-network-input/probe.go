// Fixture for bifrost.security.go.gob-decode-network-input (lead #192).
package probe

import (
	"encoding/gob"
	"net"
	"time"
)

type Request struct{ Key string }

type Reply struct{ Value string }

// Positive: a peer reached with net.Dial controls every byte the decoder reads.
func fetch(addr string) (Reply, error) {
	var r Reply
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return r, err
	}
	err = gob.NewDecoder(conn).Decode(&r)
	return r, err
}

// Positive: the same flow with the usual deferred Close.
func fetchDeferClose(addr string) (Reply, error) {
	var r Reply
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return r, err
	}
	defer conn.Close()
	err = gob.NewDecoder(conn).Decode(&r)
	return r, err
}

// Positive: a timed dial.
func fetchTimeout(addr string, timeout time.Duration) (Reply, error) {
	var r Reply
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return r, err
	}
	defer conn.Close()
	err = gob.NewDecoder(conn).Decode(&r)
	return r, err
}

// Positive: the server side from the advisory, decoding what a client sends.
func serveOne(ln net.Listener) (Request, error) {
	var req Request
	conn, err := ln.Accept()
	if err != nil {
		return req, err
	}
	defer conn.Close()
	err = gob.NewDecoder(conn).Decode(&req)
	return req, err
}

// Positive: the accepted connection is decoded by a helper.
func serveWithHelper(ln net.Listener) error {
	conn, err := ln.Accept()
	if err != nil {
		return err
	}
	defer conn.Close()
	return handle(conn)
}

func handle(conn net.Conn) error {
	var req Request
	return gob.NewDecoder(conn).Decode(&req)
}

// Near miss: an encoder over a local snapshot decodes nothing from a peer.
func encodeLocal(w snapshotWriter, req Request) error {
	return gob.NewEncoder(w).Encode(req)
}

type snapshotWriter struct{}

func (snapshotWriter) Write(p []byte) (int, error) { return len(p), nil }

type snapshot struct{}

func (snapshot) Read(p []byte) (int, error) { return 0, nil }

// Near miss: a connection is open, but the decoder reads a local snapshot.
func restoreWhileConnected(addr string) (Reply, error) {
	var r Reply
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return r, err
	}
	defer conn.Close()
	err = gob.NewDecoder(snapshot{}).Decode(&r)
	return r, err
}
