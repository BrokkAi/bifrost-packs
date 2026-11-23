use std::num::ParseIntError;

fn sink_err(_err: ParseIntError) {}

pub fn parse_unwrap_err_is_not_tainted(password: &str) {
    let parsed: Result<u32, ParseIntError> = password.parse::<u32>();
    let err: ParseIntError = parsed.unwrap_err();
    sink_err(err);
}

pub fn parse_if_let_err_is_not_tainted(password: &str) {
    let parsed: Result<u32, ParseIntError> = password.parse::<u32>();
    if let Err(err) = parsed {
        sink_err(err);
    }
}
