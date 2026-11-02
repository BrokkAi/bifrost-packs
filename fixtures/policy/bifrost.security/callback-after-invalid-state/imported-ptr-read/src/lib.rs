// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
// Known gap: unqualified imported pointer APIs are not matched.
// Expected zero; see https://github.com/BrokkAi/bifrost-dev/issues/6247.
use std::ptr;
pub unsafe fn move_then_clone<T: Clone>(slot: *mut T, f: T) {
    let _prior = ptr::read(slot);
    let _replacement = f.clone();
}
