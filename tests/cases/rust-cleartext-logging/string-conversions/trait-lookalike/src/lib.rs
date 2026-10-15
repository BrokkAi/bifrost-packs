trait Redacted {
    fn clone(&self) -> String;
    fn to_string(&self) -> String;
}
impl Redacted for String {
    fn clone(&self) -> String {
        String::from("redacted")
    }
    fn to_string(&self) -> String {
        String::from("redacted")
    }
}
pub fn custom_clone(password: String) {
    let s = Redacted::clone(&password);
    println!("{}", s);
}
pub fn custom_string(password: String) {
    let s = Redacted::to_string(&password);
    println!("{}", s);
}
