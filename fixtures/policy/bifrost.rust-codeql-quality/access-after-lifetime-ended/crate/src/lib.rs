mod pointers;

pub fn read_after_helper_returns() {
    let pointer = pointers::dangling_local();
    unsafe { core::ptr::read(pointer) };
}

pub fn live_owner_remains_valid() {
    let owner = 41;
    let pointer = pointers::live_pointer(&owner);
    unsafe { core::ptr::read(pointer) };
}
