use std::fmt::Write as _;
use std::net::TcpListener;

fn main() {
    let external_http = "http://example.com";
    let secure = "https://example.com";
    let localhost = "http://localhost";
    let loopback = "http://127.0.0.1";
    let private = "http://192.168.1.1";
    let raw_http = r"http://example.com";
    let _ = (external_http, secure, localhost, loopback, private, raw_http);

    // The authority is a format placeholder filled at run time: not selected.
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind listener");
    let address = format!("http://{}", listener.local_addr().expect("listener address"));
    let named = format!("http://{host}:{port}/", host = "h", port = 1);
    println!("http://{}", address);
    let mut out = String::new();
    write!(out, "http://{0}/path", named).expect("write url");

    // A literal external host before the placeholders is still reported.
    let external_template = format!("http://example.com/{}", 1);
    // An escaped brace is not a placeholder.
    let escaped = format!("http://{{literal}}");
    // Outside a formatting macro, the braces are not a placeholder.
    let plain_template = "http://{}";
    let _ = (external_template, escaped, plain_template, out);
}
