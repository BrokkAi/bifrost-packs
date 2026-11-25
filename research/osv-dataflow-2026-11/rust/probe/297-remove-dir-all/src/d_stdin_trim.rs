pub fn run() {
    let mut line = String::new();
    std::io::stdin().read_line(&mut line).unwrap();
    std::fs::remove_dir_all(line.trim()).unwrap();
}
