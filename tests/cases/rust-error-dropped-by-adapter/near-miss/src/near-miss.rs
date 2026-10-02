pub fn map_preserving<I>(values: I) -> Vec<Result<i32, &'static str>>
where
    I: Iterator<Item = Result<i32, &'static str>>,
{
    values.map(|result| result.map(|value| value + 1)).collect()
}

pub fn ok() -> Option<i32> {
    Some(1)
}

pub fn plain_option_call() -> Option<i32> {
    ok()
}
