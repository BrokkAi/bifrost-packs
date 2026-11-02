package main

import (
	"net/http"
	"net/url"
)

// CVE-2022-32190 shape: request data joined onto an API base on Go 1.19.0.
func handler(w http.ResponseWriter, r *http.Request) {
	u, err := url.JoinPath("https://api.example.com/v1", r.URL.Query().Get("id"))
	if err != nil {
		return
	}
	http.Get(u)
}
