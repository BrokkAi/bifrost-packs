// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Cursor<T> { pub address: *mut T }
unsafe impl<T> Send for Cursor<T> {}
