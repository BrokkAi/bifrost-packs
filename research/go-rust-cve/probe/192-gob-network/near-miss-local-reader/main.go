package main

import "encoding/gob"

type Msg struct{ A string }

type snapshot struct{}

func (snapshot) Read(p []byte) (int, error) { return 0, nil }

// Bytes the application produced itself, read through a local reader.
func restore() (Msg, error) {
	var m Msg
	err := gob.NewDecoder(snapshot{}).Decode(&m)
	return m, err
}
