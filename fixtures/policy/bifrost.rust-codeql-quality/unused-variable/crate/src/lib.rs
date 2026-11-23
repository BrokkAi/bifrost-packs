pub struct Counter {
    pub total: i32,
}

impl Counter {
    // Receiver is never reported.
    pub fn reset(&mut self) {
        self.total = 0;
    }
}

// Near miss: an initialized local is the unused-value policy's concern, not this one.
pub fn unused_local() {
    let stale = 1;
}

// Unused parameter: reported.
pub fn unused_parameter(used: i32, ignored: i32) -> i32 {
    used
}

// Unused pattern binder and loop variable: reported.
pub fn unused_binders(pair: (i32, i32), items: &[i32]) -> i32 {
    let (left, right) = pair;
    for item in items {}
    left
}

// Near misses: underscore names, used bindings and a closure parameter that is read.
pub fn near_misses(items: &[i32]) -> i32 {
    let _kept = 2;
    let used = 3;
    let total: i32 = items.iter().map(|value| value + used).sum();
    total
}
