mod application {
    pub struct MaybeUninit<T>(Option<T>);

    impl<T> MaybeUninit<T> {
        pub fn uninit() -> Self {
            Self(None)
        }

        pub fn new(value: T) -> Self {
            Self(Some(value))
        }

        pub fn write(&mut self, value: T) {
            self.0 = Some(value);
        }

        pub unsafe fn assume_init(self) -> T {
            self.0.unwrap_or_else(|| panic!("application-level empty value"))
        }
    }
}

pub fn same_spelling_different_type() -> u32 {
    let slot = application::MaybeUninit::<u32>::uninit();
    unsafe { slot.assume_init() }
}
