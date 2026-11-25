pub fn run() -> std::io::Result<()> {
    let target = std::env::var("CLEAN_DIR").unwrap();
    let result = std::fs::remove_dir_all(target);
    result
}
