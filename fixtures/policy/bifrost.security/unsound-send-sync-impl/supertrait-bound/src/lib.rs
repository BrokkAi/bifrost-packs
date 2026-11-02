// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub trait Job: Send {}
pub struct WorkItem<T>(T);
unsafe impl<T: Job> Send for WorkItem<T> {}
