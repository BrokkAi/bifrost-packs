// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct DisplaySlot<T> { item: T }
unsafe impl<T> Sync for DisplaySlot<T> {}
impl<T> DisplaySlot<T> { fn item(&self) -> &T { &self.item } }
impl<T: std::fmt::Debug> std::fmt::Debug for DisplaySlot<T> {
    fn fmt(&self, output: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        output.debug_tuple("DisplaySlot").field(self.item()).finish()
    }
}
