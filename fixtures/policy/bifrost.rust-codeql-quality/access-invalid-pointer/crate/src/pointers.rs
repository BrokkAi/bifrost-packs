use std::alloc::{alloc, dealloc, Layout};

pub fn allocate() -> *mut u32 {
    unsafe { alloc(Layout::new::<u32>()) as *mut u32 }
}

pub unsafe fn release(pointer: *mut u32) {
    unsafe { dealloc(pointer as *mut u8, Layout::new::<u32>()) };
}
