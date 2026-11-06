package probe

import (
	"net"
	"os/exec"
)

// Positive: a CNAME target chooses the program.
func runCNAME(host string) *exec.Cmd {
	name, err := net.LookupCNAME(host)
	if err != nil {
		return nil
	}
	return exec.Command(name, "-v")
}

// Positive: a TXT record chooses the program.
func runTXT(domain string) *exec.Cmd {
	txt, err := net.LookupTXT(domain)
	if err != nil || len(txt) == 0 {
		return nil
	}
	return exec.Command(txt[0])
}

// Near miss: the record is only an argument to a fixed program.
func digTXT(domain string) *exec.Cmd {
	return exec.Command("dig", domain)
}

