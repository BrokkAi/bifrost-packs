pub fn fallible() -> Result<i32, &'static str> {
    Err("source failure")
}
