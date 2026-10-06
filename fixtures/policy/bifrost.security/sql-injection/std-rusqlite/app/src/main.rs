use rusqlite::Connection as Client;

fn run(client: &mut Client, sql: &str) {
    client.execute(sql, &[]);
}

pub fn from_env_var(client: &mut Client) {
    let value: String = std::env::var("ACCOUNT").unwrap();
    let sql = "SELECT * FROM accounts WHERE name = '".to_owned() + &value + "'";
    run(client, &sql);
}

pub fn from_args(client: &mut Client) {
    let value: String = std::env::args().nth(1).unwrap();
    let sql = "SELECT * FROM accounts WHERE name = '".to_owned() + &value + "'";
    run(client, &sql);
}

pub fn from_stdin(client: &mut Client) {
    let mut line: String = String::new();
    std::io::stdin().read_line(&mut line);
    let sql = "SELECT * FROM accounts WHERE name = '".to_owned() + &line + "'";
    run(client, &sql);
}

fn main() {}
pub fn parameterized(client: &Client) {
    let value: String = std::env::var("ACCOUNT").unwrap();
    client.execute("SELECT * FROM accounts WHERE name = ?1", &[&value]);
}

pub fn non_reaching(client: &Client) {
    let _value: String = std::env::var("ACCOUNT").unwrap();
    client.execute("SELECT count(*) FROM accounts", &[]);
}
