// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub enum Pending<T> { Ready(T), Empty }
unsafe impl<T> Sync for Pending<T> {}

impl<T> Pending<T> {
    pub fn value(&self) -> Option<&T> {
        match self { Self::Ready(item) => Some(item), Self::Empty => None }
    }
}
