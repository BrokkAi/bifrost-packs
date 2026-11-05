package probe

import (
	"net/http"
	"regexp"
)

// Positive: the request chooses the pattern.
func search(r *http.Request) (*regexp.Regexp, error) {
	return regexp.Compile(r.FormValue("q"))
}

// Near miss: the request text is quoted first.
func searchQuoted(r *http.Request) (*regexp.Regexp, error) {
	return regexp.Compile(regexp.QuoteMeta(r.FormValue("q")))
}
