// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub fn prepared<F: FnMut()>(mut action: F, data: &mut Vec<u8>) {
    action();
    unsafe { data.set_len(0); }
}
