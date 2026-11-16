fn compute() -> i32 {
    4
}

// Positive: the first value is replaced before any read.
pub fn overwritten_before_read() -> i32 {
    let mut total = compute();
    total = 10;
    total
}

// Positive: the last write is never read.
pub fn never_read_after_write() {
    let mut count = 0;
    count += 1;
    count = compute();
}

// Near miss: every written value is read before it is replaced.
pub fn read_between_writes() -> i32 {
    let mut total = compute();
    let first = total;
    total = 10;
    first + total
}

// Near miss: a branch reads the value on one path and replaces it on the other.
pub fn read_on_some_path(flag: bool) -> i32 {
    let mut total = compute();
    if flag {
        return total;
    }
    total = 3;
    total
}

// Known deviation, not a near miss: CodeQL excludes underscore names, but the engine row has no
// name to filter on, so this write is reported (BrokkAi/bifrost-dev#13914).
pub fn discarded() {
    let _scratch = compute();
}
