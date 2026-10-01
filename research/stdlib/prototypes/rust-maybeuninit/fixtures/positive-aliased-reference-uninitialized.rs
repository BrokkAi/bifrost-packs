use std::mem::MaybeUninit as Slot;

pub fn reads_same_object_through_alias() -> u32 {
    let slot = Slot::<u32>::uninit();
    let alias = &slot;
    unsafe { alias.assume_init_ref().to_owned() }
}
