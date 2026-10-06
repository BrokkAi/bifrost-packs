// API-shape stub of rusqlite's Connection. It mimics the call shape only and
// claims no compatibility with a crate release.
pub struct Connection;

impl Connection {
    pub fn execute(&self, _sql: &str, _params: &[&str]) -> Result<usize, ()> {
        Ok(0)
    }
}
