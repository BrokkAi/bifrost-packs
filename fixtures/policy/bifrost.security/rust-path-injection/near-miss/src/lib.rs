use std::env;
use std::fs::{self, DirBuilder, File, OpenOptions};
use std::io;

pub fn constant_read() -> io::Result<Vec<u8>> {
    let _unused = env::var("USER_PATH").unwrap();
    fs::read("/etc/hosts")
}

pub fn constant_write_tainted_body() -> io::Result<()> {
    let raw = env::var("USER_DATA").unwrap();
    let body: &str = &raw;
    fs::write("/srv/output.txt", body)
}

pub fn constant_open_options(opts: &mut OpenOptions) -> io::Result<File> {
    let _unused = env::var("USER_PATH").unwrap();
    opts.read(true).open("/srv/fixed.txt")
}

pub fn constant_dir_builder(builder: &mut DirBuilder) -> io::Result<()> {
    let _unused = env::var("USER_PATH").unwrap();
    builder.recursive(true).create("/srv/fixed")
}

pub mod local_lookalike {
    pub struct File;
    impl File {
        pub fn open(_path: &str) -> File {
            File
        }
        pub fn create(_path: &str) -> File {
            File
        }
    }

    pub fn read(_path: &str) -> &'static [u8] {
        b""
    }

    pub fn local_fs_calls() -> (File, File, &'static [u8]) {
        let raw = std::env::var("USER_PATH").unwrap();
        let p: &str = &raw;
        (File::open(p), File::create(p), read(p))
    }
}
