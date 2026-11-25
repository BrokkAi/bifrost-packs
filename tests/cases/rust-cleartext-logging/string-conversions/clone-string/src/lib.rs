pub fn method(password: String) {
    let s = password.clone();
    println!("{}", s);
}
pub fn qualified(password: String) {
    let s = <String as std::clone::Clone>::clone(&password);
    println!("{}", s);
}
pub fn encrypted(encrypted_password: String) {
    let s = encrypted_password.clone();
    println!("{}", s);
}
