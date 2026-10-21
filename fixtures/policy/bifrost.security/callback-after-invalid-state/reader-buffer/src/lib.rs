// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
use std::io::Read;
pub fn receive<R: Read>(mut reader: R, count: usize) -> std::io::Result<Vec<u8>> {
    let mut buf = Vec::with_capacity(count);
    unsafe { buf.set_len(count); }
    reader.read(&mut buf)?;
    Ok(buf)
}
