fn println(_: &str) {}
fn eprintln(_: &str) {}
fn panic_fmt(_: &str) {}
struct Writer;
impl Writer { fn write(&self, _: &str) {} }
pub fn innocent(password: &str) {
    std::println!("safe");
    println(password);
    eprintln(password);
    panic_fmt(password);
    Writer.write(password);
}

mod shadowed_macro {
    macro_rules! println { ($($arg:tt)*) => {}; }
    pub fn innocent_macro(password: &str) {
        println!("{}", password);
    }
}
