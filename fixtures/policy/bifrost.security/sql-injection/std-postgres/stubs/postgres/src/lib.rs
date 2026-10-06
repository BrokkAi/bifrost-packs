// API-shape stub of the postgres crate's synchronous client. It mimics the
// call shape only and claims no compatibility with a crate release.
mod client {
    pub struct Client;

    impl Client {
        pub fn execute(&mut self, _query: &str, _params: &[&str]) -> Result<u64, ()> {
            Ok(0)
        }
    }
}

pub use client::Client;
