# Go 1 applicability of io declaration facts

`bifrost.go.stdlib.io-declarations` selects released Go toolchains
`>=1.26.0, <2.0.0`. Its partial inventory certifies the 22 exported
interfaces declared in `io/io.go`, their methods and embedded interfaces.
It does not claim every `io` member, runtime behavior, ABI compatibility,
or unchanged future package inventories.

The declarations have Go 1.26.0 provenance: [io.go at the immutable Go 1.26.0
source revision](https://github.com/golang/go/blob/d90b98e65320778f3b1f99a6951ab20f04d218b3/src/io/io.go).
The [Go 1 compatibility document](https://go.dev/doc/go1compat) establishes
a source-compatibility expectation for Go 1 standard packages. It also allows
security fixes, corrections to unspecified behavior and bugs, and additions to
exported structs and methods; dot imports may acquire new name collisions.
The range above selects these published interface declarations under that
source-compatibility expectation. It does not qualify actual call bindings or
consumer behavior.
