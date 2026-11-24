use std::env;
use std::fs::{self, File};
use std::io;

pub fn env_args_read() -> io::Result<Vec<u8>> {
    let raw = env::args().nth(1).unwrap();
    let p: &str = &raw;
    fs::read(p)
}

pub fn stdin_file_open() -> io::Result<File> {
    let mut line = String::new();
    let _ = io::stdin().read_line(&mut line);
    let p: &str = &line;
    File::open(p)
}
