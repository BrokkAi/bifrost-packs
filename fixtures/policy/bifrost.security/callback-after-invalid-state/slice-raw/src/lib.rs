// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn expose<F: FnMut()>(ptr: *mut u8, mut action: F) {
    let _slice = std::slice::from_raw_parts_mut(ptr, 4);
    action();
}
