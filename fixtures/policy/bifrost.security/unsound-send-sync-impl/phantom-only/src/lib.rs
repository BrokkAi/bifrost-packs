// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
use std::marker::PhantomData;
pub struct TypeTag<T>(PhantomData<T>);
unsafe impl<T> Send for TypeTag<T> {}
