// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
use crate::SharedSlot;
impl<T> SharedSlot<T> { pub fn item(&self) -> &T { &self.item } }
