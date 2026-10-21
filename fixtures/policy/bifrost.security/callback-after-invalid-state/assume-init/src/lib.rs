// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn unpack<F: FnMut()>(cell: std::mem::MaybeUninit<u8>, mut action: F) {
    let _value = cell.assume_init();
    action();
}
