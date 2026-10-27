package example
func example() {
 run("a") // $ Alert[go/command-injection]
 run("b") // $ Alert[go/stored-command]
 run("c") // $ Source Alert
 run("d") // $ Source Alert[go/command-injection], Alert[go/stored-command]
 run("e") // $ Alert[go/stored-command] MISSING: Alert[go/command-injection]
 run("f") // $ SPURIOUS: Alert[go/stored-command] // remark: $ Alert
}
