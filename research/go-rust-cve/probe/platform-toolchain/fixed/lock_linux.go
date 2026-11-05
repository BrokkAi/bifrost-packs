//go:build linux

package main

import "os"

// Never built for Windows: filename suffix and build line both say linux.
func lockLinux(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
}
