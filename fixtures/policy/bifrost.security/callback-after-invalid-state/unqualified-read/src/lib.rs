// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub fn read() {}
pub fn ordinary<F: FnMut()>(mut action: F) {
    read();
    action();
}
