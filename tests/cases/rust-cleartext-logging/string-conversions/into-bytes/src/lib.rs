pub fn method(password: String) {
    let s = password.into_bytes();
    println!("{:?}", s);
}
pub fn encrypted(encrypted_password: String) {
    let s = encrypted_password.into_bytes();
    println!("{:?}", s);
}
