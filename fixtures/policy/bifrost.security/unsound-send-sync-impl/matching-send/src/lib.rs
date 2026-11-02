// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Transfer<T>(T);
unsafe impl<T: Send> Send for Transfer<T> {}
