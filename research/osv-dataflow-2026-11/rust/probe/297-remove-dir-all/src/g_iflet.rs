pub fn run() {
    if let Ok(target) = std::env::var("CLEAN_DIR") {
        let _ = std::fs::remove_dir_all(target);
    }
}
