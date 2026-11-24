use std::env;
use std::process::Command;

fn forward(raw: &str) -> &str {
    raw
}

pub fn env_var_to_command_new() -> Command {
    let raw = env::var("USER_CMD").unwrap();
    let prog: &str = &raw;
    Command::new(prog)
}

pub fn env_var_helper_to_command_new() -> Command {
    let raw = env::var("USER_CMD").unwrap();
    let prog: &str = &raw;
    Command::new(forward(prog))
}

pub fn env_var_to_command_arg(cmd: &mut Command) -> &mut Command {
    let raw = env::var("USER_ARG").unwrap();
    let arg: &str = &raw;
    cmd.arg(arg)
}

pub fn env_var_to_chained_command_arg(cmd: &mut Command) -> &mut Command {
    let raw = env::var("USER_ARG").unwrap();
    let arg: &str = &raw;
    cmd.arg("-c").arg(arg)
}

pub fn env_var_to_command_args(cmd: &mut Command) -> &mut Command {
    let raw = env::var("USER_ARG").unwrap();
    let arg: &str = &raw;
    let extra = [arg];
    cmd.args(extra)
}

pub fn env_var_to_chained_command_args(cmd: &mut Command) -> &mut Command {
    let raw = env::var("USER_ARG").unwrap();
    let arg: &str = &raw;
    let extra = [arg];
    cmd.arg("--").args(extra)
}
