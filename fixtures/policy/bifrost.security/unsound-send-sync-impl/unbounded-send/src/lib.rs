// SPDX-License-Identifier: Apache-2.0
// Authored public fixture; analysis only, never execute.
pub struct Parcel<T>(T);
unsafe impl<T> Send for Parcel<T> {}
