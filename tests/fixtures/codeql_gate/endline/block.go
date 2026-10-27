package example
func example() {
 if a {
  println("x")
  println("y")
 } // $ Alert
 for {
  if b {
   println("z")
  } // $ SPURIOUS: Alert
 }
 switch {
 case c:
 } // $ Alert
}
