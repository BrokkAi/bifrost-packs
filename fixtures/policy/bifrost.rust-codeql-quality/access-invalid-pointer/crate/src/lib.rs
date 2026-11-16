mod pointers;

pub fn read_after_release() {
    let pointer = pointers::allocate();
    unsafe { pointers::release(pointer) };
    unsafe { core::ptr::read(pointer) };
}

pub fn read_before_release() {
    let pointer = pointers::allocate();
    let value = unsafe {
        // The read at line 13 still precedes this pointer's release.
        core::ptr::read(pointer)
    };
    let _ = value;
    unsafe { pointers::release(pointer) };
}
