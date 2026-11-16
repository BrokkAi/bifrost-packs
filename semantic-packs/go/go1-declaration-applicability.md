# Go 1 applicability of reviewed declaration facts

`bifrost.go.stdlib.net-http-declarations` and
`bifrost.go.stdlib.database-sql-declarations` select released Go toolchains
`>=1.26.0, <2.0.0`. This applicability is for the direct public declarations
listed in those partial packs. It is not a complete inventory of either
package, a behavior or ABI model, or an assertion about prerelease builds.

The declared `net/http.Request.FormValue` type and signature come from the
immutable Go 1.26.0 source at
[request.go](https://github.com/golang/go/blob/d90b98e65320778f3b1f99a6951ab20f04d218b3/src/net/http/request.go).
The `database/sql` DB, Tx, Stmt and Result types and three Exec signatures
come from [sql.go](https://github.com/golang/go/blob/d90b98e65320778f3b1f99a6951ab20f04d218b3/src/database/sql/sql.go).
The declaration models retain their own Go 1.26.0 provenance and BSD notice;
this note supplies the separate cross-release applicability authority.

The [Go 1 compatibility document](https://go.dev/doc/go1compat) states the
source-compatibility expectation for Go 1 standard packages and describes its
exceptions, including security fixes, unspecified behavior, specification and
library bug fixes, additions to exported structs and methods, and dot-import
name collisions. It does not promise binary compatibility or unchanged
behavior. The range above is a bounded source-declaration selection rule for
these published APIs, subject to those documented exceptions. Qualification
of an activated pack and actual call bindings remains a separate requirement.
