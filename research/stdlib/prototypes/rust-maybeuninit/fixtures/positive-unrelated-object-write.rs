use std::mem::MaybeUninit;

pub fn write_to_another_object() -> u32 {
    let slot = MaybeUninit::<u32>::uninit();
    let mut other = MaybeUninit::<u32>::uninit();
    other.write(42);
    unsafe { slot.assume_init() }
}
