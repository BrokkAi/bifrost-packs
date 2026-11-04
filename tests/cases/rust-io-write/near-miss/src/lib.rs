use std::fs::File;
use std::io::Write;

pub fn persist_to_file(file: &mut File) {
    let password = "fixture-secret";
    let _written = file.write(password.as_bytes());
    let _all = file.write_all(password.as_bytes());
    let _formatted = file.write_fmt(format_args!("{password}"));
}
