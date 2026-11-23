use std::num::ParseIntError;

fn sink_u32(_value: u32) {}
fn sink_bool(_flag: bool) {}

pub fn parse_try_ok_flows(password: &str) -> Result<(), ParseIntError> {
    let parsed: u32 = password.parse::<u32>()?;
    sink_u32(parsed);
    Ok(())
}

pub fn parse_unwrap_ok_flows(password: &str) {
    let parsed: Result<u32, ParseIntError> = password.parse::<u32>();
    let value: u32 = parsed.unwrap();
    sink_u32(value);
}

pub fn parse_unwrap_or_ok_flows(password: &str) {
    let parsed: Result<u32, ParseIntError> = password.parse::<u32>();
    let fallback: u32 = 0;
    let value: u32 = parsed.unwrap_or(fallback);
    sink_u32(value);
}

pub fn unwrap_or_default_arg_flows(password_code: u32, clean: Result<u32, ParseIntError>) {
    let value: u32 = clean.unwrap_or(password_code);
    sink_u32(value);
}

pub fn parse_unwrap_or_default_flows(password: &str) {
    let parsed: Result<u32, ParseIntError> = password.parse::<u32>();
    let value: u32 = parsed.unwrap_or_default();
    sink_u32(value);
}

pub fn metadata_is_dir_flows(secret_meta: &std::fs::Metadata) {
    let flag: bool = secret_meta.is_dir();
    sink_bool(flag);
}
