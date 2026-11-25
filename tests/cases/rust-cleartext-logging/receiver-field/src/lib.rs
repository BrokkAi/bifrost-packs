pub struct Secret(String);

impl Secret {
    pub fn inner(&self) -> &str {
        self.0.as_str()
    }
}

pub struct Config {
    pub api_key: Secret,
}

impl Config {
    pub fn direct(&self) {
        println!("Honeycomb API key: {}", self.api_key.inner());
    }

    pub fn through_local(&self) {
        let message = self.api_key.inner();
        println!("{}", message);
    }
}

pub struct EncryptedConfig {
    pub encrypted_api_key: Secret,
}

impl EncryptedConfig {
    pub fn near_miss(&self) {
        let message = self.encrypted_api_key.inner();
        println!("{}", message);
    }
}

pub fn binder_only(password: &str) {
    println!("constant");
}
