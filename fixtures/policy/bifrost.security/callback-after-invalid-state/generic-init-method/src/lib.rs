// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Buf<T> { data: Vec<T> }
impl<T> Buf<T> {
    pub fn fill<F: FnMut(usize) -> T>(&mut self, count: usize, mut init: F) {
        self.data.reserve(count);
        unsafe { self.data.set_len(count); }
        for i in 0..count { self.data[i] = init(i); }
    }
}
