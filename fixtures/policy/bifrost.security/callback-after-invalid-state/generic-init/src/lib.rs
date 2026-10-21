// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub fn fill<F: FnMut(usize) -> u8>(count: usize, mut init: F) -> Vec<u8> {
    let mut data = Vec::with_capacity(count);
    unsafe { data.set_len(count); }
    for i in 0..count { data[i] = init(i); }
    data
}
