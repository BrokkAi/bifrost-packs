// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
fn checkpoint() {}
pub struct Buf<T> { data: Vec<T> }
impl<T> Buf<T> {
    pub fn trimmed(&mut self) {
        unsafe { self.data.set_len(0); }
        checkpoint();
    }
}
