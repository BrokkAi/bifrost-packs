pub fn run() {
    let target = std::env::args().nth(1).unwrap();
    std::fs::remove_dir_all(target).unwrap();
}
