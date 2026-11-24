use std::env;
use std::io;
use std::process::Command;

pub fn env_args_to_command_new() -> Command {
    let raw = env::args().nth(1).unwrap();
    let prog: &str = &raw;
    Command::new(prog)
}

pub fn stdin_to_command_arg(cmd: &mut Command) -> &mut Command {
    let mut line = String::new();
    let _ = io::stdin().read_line(&mut line);
    let arg: &str = &line;
    cmd.arg(arg)
}
