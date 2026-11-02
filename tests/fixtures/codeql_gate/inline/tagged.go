package example
func example() {
 println("alert") // $ Alert
 println("bracket") // $ Alert[example]
 println("taint") // $ hasTaintFlow="source"
 println("source") // $ Source
 println("sink") // $ Sink
 println(`// $ Alert`)
 println("// $ Alert")
 /* // $ Alert */
}
