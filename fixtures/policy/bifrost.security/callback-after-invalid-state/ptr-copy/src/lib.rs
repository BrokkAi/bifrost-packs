// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn duplicate<F: FnMut()>(src: *const u8, dst: *mut u8, mut action: F) {
    std::ptr::copy(src, dst, 1);
    action();
}
