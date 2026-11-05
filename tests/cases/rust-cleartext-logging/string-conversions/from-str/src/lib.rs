pub fn method(password: &str) {
    let s = String::from(password);
    println!("{}", s);
}
pub fn qualified(password: &str) {
    let s = <String as std::convert::From<&str>>::from(password);
    println!("{}", s);
}
pub fn encrypted(encrypted_password: &str) {
    let s = String::from(encrypted_password);
    println!("{}", s);
}
