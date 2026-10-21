// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn duplicate_disjoint<F: FnMut()>(src: *const u8, dst: *mut u8, mut action: F) {
    core::ptr::copy_nonoverlapping(src, dst, 1);
    action();
}
