use std::mem::MaybeUninit;

unsafe extern "C" {
    fn opaque_maybe_initialize(slot: *mut MaybeUninit<u32>);
}

pub fn escapes_before_consuming() -> u32 {
    let mut slot = MaybeUninit::<u32>::uninit();
    unsafe { opaque_maybe_initialize(slot.as_mut_ptr()) };
    unsafe { slot.assume_init() }
}
