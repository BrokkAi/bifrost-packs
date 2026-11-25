package main

import (
	"net/http"
	"os"
)

// Platform-neutral file: built for every GOOS, Windows included.
func lockNeutral(path string) (*os.File, error) {
	return os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
}

func main() {
	http.Handle("/static/", http.FileServer(http.Dir("public")))
	_, _ = lockNeutral(os.Args[1])
}
