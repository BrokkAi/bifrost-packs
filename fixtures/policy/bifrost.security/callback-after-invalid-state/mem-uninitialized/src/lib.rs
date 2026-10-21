// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn legacy<F: FnMut()>(mut action: F) {
    let _value: u8 = std::mem::uninitialized();
    action();
}
