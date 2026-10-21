// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn raw_receiver<F: FnMut()>(ptr: *const u8, mut action: F) {
    let _prior = ptr.read();
    action();
}
