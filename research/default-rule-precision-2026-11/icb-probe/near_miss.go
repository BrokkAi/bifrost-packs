package fixture

func Ladder(scheme string, port int, host string, out []string) []string {
	if scheme == "http" || port == 80 {
		out = append(out, "http")
	} else if scheme == "https" || port == 443 {
		out = append(out, "https")
	} else if host == "" {
		out = append(out, "http")
	}
	return out
}
