use std::alloc::{self, Layout};
use std::env;

pub unsafe fn constant_alloc() -> *mut u8 {
    let _unused = env::var("USER_DATA").unwrap();
    let layout = Layout::from_size_align_unchecked(64, 8);
    alloc::alloc(layout)
}

pub unsafe fn constant_realloc(ptr: *mut u8, layout: Layout) -> *mut u8 {
    let _unused = env::var("USER_DATA").unwrap();
    alloc::realloc(ptr, layout, 128)
}

pub mod local_lookalike {
    pub fn alloc(_size: usize) -> *mut u8 {
        core::ptr::null_mut()
    }

    pub fn realloc(_ptr: *mut u8, _old: usize, _new_size: usize) -> *mut u8 {
        core::ptr::null_mut()
    }

    pub fn local_alloc_calls(ptr: *mut u8) -> (*mut u8, *mut u8) {
        let raw = std::env::var("USER_DATA").unwrap();
        let s: &str = &raw;
        let size: usize = s.len();
        (alloc(size), realloc(ptr, 8, size))
    }
}
