use std::mem::MaybeUninit;

pub fn only_initialized_on_one_branch(flag: bool) -> u32 {
    let mut slot = MaybeUninit::<u32>::uninit();
    if flag {
        slot.write(42);
    }
    unsafe { slot.assume_init() }
}
