use std::alloc::{self, Layout};
use std::env;

pub unsafe fn env_len_to_realloc(ptr: *mut u8, layout: Layout) -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let new_size: usize = s.len();
    alloc::realloc(ptr, layout, new_size)
}

pub unsafe fn env_len_to_alloc_via_unchecked_layout() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let size: usize = s.len();
    let layout = Layout::from_size_align_unchecked(size, 8);
    alloc::alloc(layout)
}

pub unsafe fn env_len_to_alloc_zeroed_via_layout() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let size: usize = s.len();
    let layout = Layout::from_size_align(size, 8).unwrap();
    alloc::alloc_zeroed(layout)
}

pub unsafe fn env_len_to_alloc_via_layout_array() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let count: usize = s.len();
    let layout = Layout::array::<u64>(count).unwrap();
    alloc::alloc(layout)
}

pub unsafe fn env_len_to_alloc_via_layout_pad() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let size: usize = s.len();
    let layout = Layout::from_size_align_unchecked(size, 4).pad_to_align();
    alloc::alloc(layout)
}

pub unsafe fn env_len_to_alloc_zeroed_via_layout_align_to() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let size: usize = s.len();
    let layout = Layout::from_size_align_unchecked(size, 4).align_to(16).unwrap();
    alloc::alloc_zeroed(layout)
}

pub unsafe fn env_len_to_alloc_via_layout_repeat_packed() -> *mut u8 {
    let raw = env::var("USER_DATA").unwrap();
    let s: &str = &raw;
    let count: usize = s.len();
    let base = Layout::from_size_align_unchecked(8, 8);
    let layout = base.repeat_packed(count).unwrap();
    alloc::alloc(layout)
}
