// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn shrink(data: &mut Vec<u8>) { data.set_len(0); }
pub fn run<F: FnMut()>(mut action: F) { action(); }
