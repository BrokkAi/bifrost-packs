# Public Rust CodeQL quality fixtures

The constructor fixture checks a constructor reaching a standard-library call through a helper, with a libc-only helper and a destructor as near misses. The unused-variable candidate probe is intentionally omitted because it does not prove the no-read/no-initializer predicate.
