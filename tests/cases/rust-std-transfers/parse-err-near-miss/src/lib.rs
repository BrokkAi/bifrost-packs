fn sink_err(_err: u32) {}

pub fn parse_err_is_not_tainted(password: &str) {
    let parsed: Result<u32, u32> = password.parse::<u32>();
    let err: u32 = parsed.unwrap_err();
    sink_err(err);
}
