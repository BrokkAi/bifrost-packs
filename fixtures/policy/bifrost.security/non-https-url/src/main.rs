fn main() {
    let external_http = "http://example.com";
    let secure = "https://example.com";
    let localhost = "http://localhost";
    let loopback = "http://127.0.0.1";
    let private = "http://192.168.1.1";
    let raw_http = r"http://example.com";
    let _ = (external_http, secure, localhost, loopback, private, raw_http);
}
