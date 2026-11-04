use std::io::{self, Write};

pub fn disclose_to_console() {
    let password = "fixture-secret";
    let stdout = io::stdout();
    let mut stdout = stdout.lock();
    let _written = stdout.write(password.as_bytes());
    let _all = stdout.write_all(password.as_bytes());

    let stderr = io::stderr();
    let mut stderr = stderr.lock();
    let _all = stderr.write_all(password.as_bytes());
}
