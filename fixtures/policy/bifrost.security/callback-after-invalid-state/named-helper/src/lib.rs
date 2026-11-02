// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
fn checkpoint() {}
pub fn trimmed(data: &mut Vec<u8>) {
    unsafe { data.set_len(0); }
    checkpoint();
}
