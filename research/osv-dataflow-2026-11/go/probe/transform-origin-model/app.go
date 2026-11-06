package repro

import (
	"compress/gzip"
	"io"
)

func input() io.Reader { return nil }
func sink(r io.Reader) {}

// transform on a model-summarized call
func RunModel() {
	zr, err := gzip.NewReader(input())
	if err != nil {
		return
	}
	sink(zr)
}
