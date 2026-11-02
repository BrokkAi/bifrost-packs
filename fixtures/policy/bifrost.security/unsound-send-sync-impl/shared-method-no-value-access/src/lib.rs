// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct OwnedJob<T> { payload: T, sequence: usize }
unsafe impl<T> Sync for OwnedJob<T> {}
impl<T> OwnedJob<T> {
    pub fn sequence(&self) -> usize { self.sequence }
    pub fn finish(self) -> T { self.payload }
    pub fn replace(&mut self, payload: T) { self.payload = payload; }
}
