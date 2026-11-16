pub fn print_secret(password: &str) {
    println!("{}", password);
    std::eprintln!("{}", password);
}
pub struct Config { pub api_key: String }
pub fn field_secret(config: &Config) {
    println!("{}", config.api_key);
}
