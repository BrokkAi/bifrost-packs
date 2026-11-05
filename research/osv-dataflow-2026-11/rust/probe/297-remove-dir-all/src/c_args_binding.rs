pub fn run() {
    let mut args = std::env::args();
    let target = args.nth(1).unwrap();
    std::fs::remove_dir_all(target).unwrap();
}
