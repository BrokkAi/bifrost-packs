#[ctor::ctor]
pub fn bad_ctor() {
    std_helper();
}

#[ctor::ctor]
pub fn good_ctor() {
    libc_helper();
}

#[dtor::dtor]
pub fn good_dtor() {}

pub fn std_helper() {
    let _ = std::fs::read("startup-state");
}

pub fn libc_helper() {
    let value: u8 = 0;
    unsafe {
        let _ = libc::write(1, &value, 1);
    }
}

pub fn ordinary_helper() {}
