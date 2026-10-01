use std::mem::MaybeUninit;

pub fn consumes_uninitialized() -> u32 {
    let slot = MaybeUninit::<u32>::uninit();
    unsafe { slot.assume_init() }
}
