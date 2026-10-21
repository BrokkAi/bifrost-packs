// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
fn run<F: FnOnce()>(body: F) { body(); }
pub fn fill<F: FnMut(usize) -> u8>(data: &mut Vec<u8>, count: usize, mut init: F) {
    run(|| {
        data.reserve(count);
        unsafe { data.set_len(count); }
        for i in 0..count { data[i] = init(i); }
    });
}
