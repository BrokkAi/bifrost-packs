package probe

import (
	"net"
	"os/exec"
)

func collect(host string) []*exec.Cmd {
	name, _ := net.LookupCNAME(host)
	c := exec.Command(name, "-v")
	var out []*exec.Cmd
	out = append(out, c)
	return out
}
