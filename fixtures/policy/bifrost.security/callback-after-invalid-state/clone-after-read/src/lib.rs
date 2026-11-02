// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub unsafe fn replace<T: Clone>(slot: *mut T, f: T) {
    let previous = std::ptr::read(slot);
    let replacement = f.clone();
    slot.write(replacement);
    drop(previous);
}
