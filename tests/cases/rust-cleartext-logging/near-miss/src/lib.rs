pub fn safe(encrypted_password: &str, hashed_password: &str, secret_path: &str) {
    println!("{} {} {}", encrypted_password, hashed_password, secret_path);
}
