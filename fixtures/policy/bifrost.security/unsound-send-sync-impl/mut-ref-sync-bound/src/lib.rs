// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Exclusive<'a, T>(&'a mut T);
unsafe impl<'a, T: Sync> Send for Exclusive<'a, T> {}
