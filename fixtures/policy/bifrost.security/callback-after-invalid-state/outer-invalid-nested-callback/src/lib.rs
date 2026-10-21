// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub fn repaired<F: FnMut()>(data: &mut Vec<u8>, count: usize, mut callback: F) {
    data.reserve(count);
    unsafe { data.set_len(count); }
    let mut observe = || callback();
    // Repair the logical length before invoking the nested callback.
    unsafe { data.set_len(0); }
    observe();
}
