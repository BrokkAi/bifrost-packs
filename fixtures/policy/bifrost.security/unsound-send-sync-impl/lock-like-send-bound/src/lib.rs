// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Guarded<T>(std::sync::Mutex<T>);
unsafe impl<T: Send> Sync for Guarded<T> {}
