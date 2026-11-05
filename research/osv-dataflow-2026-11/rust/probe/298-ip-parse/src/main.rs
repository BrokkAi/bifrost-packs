use std::net::Ipv4Addr;
use std::str::FromStr;

fn denied(ip: Ipv4Addr) -> bool {
    ip == Ipv4Addr::new(10, 0, 0, 1)
}

fn main() {
    let raw = std::env::var("CLIENT_IP").unwrap();
    let a: Ipv4Addr = raw.parse().unwrap();
    let b = Ipv4Addr::from_str(&raw).unwrap();
    let c = raw.parse::<Ipv4Addr>().unwrap();
    if denied(a) || denied(b) || denied(c) {
        std::process::exit(1);
    }
}
