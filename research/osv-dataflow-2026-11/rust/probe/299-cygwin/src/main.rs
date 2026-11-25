use std::path::{Component, Path};

fn main() {
    let name = std::env::var("REQUESTED").unwrap();
    let rel = Path::new(&name);
    if rel.components().any(|c| c == Component::ParentDir) {
        return;
    }
    let _ = std::fs::read(Path::new("/srv/files").join(rel));
}
