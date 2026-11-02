use std::process::Command;

// CVE-2024-24576 shape: an argument from the command line passed to a batch file.
fn main() {
    let arg = std::env::args().nth(1).unwrap_or_default();
    let _ = Command::new("run.bat").arg(arg).status();
}
