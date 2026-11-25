package main

import "os"

// Windows-only file (filename suffix).
func lockWindows(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
}
