// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
use std::marker::PhantomData;
pub struct FactoryTag<T>(PhantomData<fn() -> T>);
unsafe impl<T> Sync for FactoryTag<T> {}
