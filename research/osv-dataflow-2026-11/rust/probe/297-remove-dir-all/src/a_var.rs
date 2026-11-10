pub fn run() {
    let target = std::env::var("CLEAN_DIR").unwrap();
    std::fs::remove_dir_all(target).unwrap();
}
