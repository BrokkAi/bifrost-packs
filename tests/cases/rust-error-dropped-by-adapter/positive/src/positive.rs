pub fn drop_error() -> Option<i32> {
    crate::sources::fallible().ok()
}

pub fn filter_results<I>(values: I) -> Vec<i32>
where
    I: Iterator<Item = Result<i32, &'static str>>,
{
    values.filter_map(Result::ok).collect()
}

pub fn flatten_results<I>(values: I) -> Vec<i32>
where
    I: Iterator<Item = Result<i32, &'static str>>,
{
    values.flatten().collect()
}
