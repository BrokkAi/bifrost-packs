// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub enum Pending<T> { Ready(T), Empty }
unsafe impl<T> Sync for Pending<T> {}
