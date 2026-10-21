// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct SharedValue<T>(T);
unsafe impl<T: Sync> Sync for SharedValue<T> {}
