pub(crate) fn recurse(input: &[u8]) -> usize {
    if let [_, tail @ ..] = input {
        1 + recurse(tail)
    } else {
        0
    }
}

pub fn parse(input: &[u8]) -> usize {
    recurse(input)
}

pub(crate) fn recurse_text(input: &str) -> usize {
    let _ = input;
    recurse_text(input)
}
