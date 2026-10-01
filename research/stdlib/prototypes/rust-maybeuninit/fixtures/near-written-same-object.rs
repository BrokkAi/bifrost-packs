use std::mem::MaybeUninit;

pub fn initializes_same_object() -> u32 {
    let mut slot = MaybeUninit::<u32>::uninit();
    slot.write(42);
    unsafe { slot.assume_init() }
}
