// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub fn local(data: &mut Vec<u8>) {
    unsafe { data.set_len(0); }
    let observe = || 7;
    let _ = observe();
}
