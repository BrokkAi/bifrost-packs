// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Borrowed<'a, T>(&'a T);
unsafe impl<'a, T: Sync> Send for Borrowed<'a, T> {}
