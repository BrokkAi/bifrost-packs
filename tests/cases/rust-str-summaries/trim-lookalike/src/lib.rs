struct Padded(String);
impl Padded {
    fn trim(&self) -> &str {
        "redacted"
    }
}
pub fn custom_trim(password: String) {
    let p = Padded(password);
    println!("{}", p.trim());
}
