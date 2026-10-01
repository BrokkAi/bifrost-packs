use std::mem::MaybeUninit;

pub fn constructor_starts_initialized() -> u32 {
    let slot = MaybeUninit::new(42_u32);
    unsafe { slot.assume_init() }
}
