// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
mod reader;
pub struct SharedSlot<T> { item: T }
unsafe impl<T> Sync for SharedSlot<T> {}
