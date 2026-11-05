pub fn boolean(password_present: bool) {
    println!("{}", password_present);
}
#[derive(Debug)]
pub enum Status { Active, Inactive }
pub fn fieldless_enum(secret_state: Status) {
    println!("{:?}", secret_state);
}
