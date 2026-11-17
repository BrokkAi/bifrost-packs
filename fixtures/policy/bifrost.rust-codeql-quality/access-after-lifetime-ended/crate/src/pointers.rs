pub fn dangling_local() -> *const u32 {
    let local = 7;
    &local as *const u32
}

pub fn live_pointer(value: &u32) -> *const u32 {
    value as *const u32
}
