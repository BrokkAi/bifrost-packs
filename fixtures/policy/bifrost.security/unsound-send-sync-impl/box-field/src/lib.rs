// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct OwnedSlot<T>(Box<T>);
unsafe impl<T> Send for OwnedSlot<T> {}
