package repro

import "os/exec"

func input() string { return "" }

// The variadic parameter receives no argument.
func NoVariadic() *exec.Cmd { return exec.Command(input()) }
