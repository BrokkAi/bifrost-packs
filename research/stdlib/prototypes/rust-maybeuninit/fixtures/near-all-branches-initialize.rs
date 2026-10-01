use std::mem::MaybeUninit;

pub fn initialized_on_each_branch(flag: bool) -> u32 {
    let mut slot = MaybeUninit::<u32>::uninit();
    if flag {
        slot.write(42);
    } else {
        slot.write(7);
    }
    unsafe { slot.assume_init() }
}
