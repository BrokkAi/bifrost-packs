pub fn run() {
    let _home = std::env::var("HOME").unwrap();
    std::fs::remove_dir_all("target/tmp-cache").unwrap();
}
