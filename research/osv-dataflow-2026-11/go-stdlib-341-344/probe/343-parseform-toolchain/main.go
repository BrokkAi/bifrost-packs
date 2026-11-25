package main

import (
	"fmt"
	"net/http"
)

// subscribe parses an URL-encoded body. Go before 1.24.12 and 1.25.0–1.25.5
// allocate one map entry per distinct key with no count limit
// (CVE-2025-61726).
func subscribe(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseForm(); err != nil {
		http.Error(w, "bad form", http.StatusBadRequest)
		return
	}
	fmt.Fprintln(w, len(r.Form))
}

func main() {
	http.HandleFunc("/subscribe", subscribe)
	_ = http.ListenAndServe(":8080", nil)
}
