pub fn parse(input: &[u8]) -> usize {
    crate::parser::parse(input)
}

pub fn parse_text(input: &str) -> usize {
    crate::parser::recurse_text(input)
}
