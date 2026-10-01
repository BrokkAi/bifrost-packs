use std::mem::MaybeUninit;

fn initialize(slot: &mut MaybeUninit<u32>) {
    slot.write(42);
}

pub fn consumes_helper_initialized_value() -> u32 {
    let mut slot = MaybeUninit::<u32>::uninit();
    initialize(&mut slot);
    unsafe { slot.assume_init() }
}
