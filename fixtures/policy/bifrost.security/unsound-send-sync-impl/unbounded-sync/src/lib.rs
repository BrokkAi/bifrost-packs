// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Snapshot<T> { pub value: T }
unsafe impl<T> Sync for Snapshot<T> {}

impl<T> Snapshot<T> { pub fn get(&self) -> &T { &self.value } }
