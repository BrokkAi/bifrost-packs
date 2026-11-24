use std::env;
use std::fs::{self, DirBuilder, File, OpenOptions};
use std::io;

fn forward(raw: &str) -> &str {
    raw
}

pub fn read_path() -> io::Result<Vec<u8>> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::read(p)
}

pub fn read_to_string_path() -> io::Result<String> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::read_to_string(forward(p))
}

pub fn write_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::write(p, b"data")
}

pub fn copy_src_path() -> io::Result<u64> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::copy(p, "/srv/dst")
}

pub fn copy_dst_path() -> io::Result<u64> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::copy("/srv/src", p)
}

pub fn rename_src_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::rename(p, "/srv/dst")
}

pub fn rename_dst_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::rename("/srv/src", p)
}

pub fn hard_link_src_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::hard_link(p, "/srv/link")
}

pub fn hard_link_dst_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::hard_link("/srv/orig", p)
}

pub fn create_dir_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::create_dir(p)
}

pub fn create_dir_all_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::create_dir_all(p)
}

pub fn remove_file_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::remove_file(p)
}

pub fn remove_dir_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::remove_dir(p)
}

pub fn remove_dir_all_path() -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::remove_dir_all(p)
}

pub fn metadata_path() -> io::Result<fs::Metadata> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::metadata(p)
}

pub fn symlink_metadata_path() -> io::Result<fs::Metadata> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::symlink_metadata(p)
}

pub fn read_dir_path() -> io::Result<fs::ReadDir> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::read_dir(p)
}

pub fn read_link_path() -> io::Result<std::path::PathBuf> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    fs::read_link(p)
}

pub fn file_open_path() -> io::Result<File> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    File::open(p)
}

pub fn file_create_path() -> io::Result<File> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    File::create(p)
}

pub fn file_create_new_path() -> io::Result<File> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    File::create_new(p)
}

pub fn open_options_path(opts: &mut OpenOptions) -> io::Result<File> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    opts.read(true).open(p)
}

pub fn dir_builder_path(builder: &mut DirBuilder) -> io::Result<()> {
    let raw = env::var("USER_PATH").unwrap();
    let p: &str = &raw;
    builder.recursive(true).create(p)
}
