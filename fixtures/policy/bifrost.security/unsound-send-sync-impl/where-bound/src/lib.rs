// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Outbox<T>(T);
unsafe impl<T> Send for Outbox<T> where T: Send {}
