use std::env;
use std::process::Command;

pub fn constant_command_new() -> Command {
    let _unused = env::var("USER_CMD").unwrap();
    Command::new("ls")
}

pub fn constant_command_arg(cmd: &mut Command) -> &mut Command {
    let _unused = env::var("USER_ARG").unwrap();
    cmd.arg("-la")
}

pub fn constant_command_args(cmd: &mut Command) -> &mut Command {
    let _unused = env::var("USER_ARG").unwrap();
    let safe_args = ["/tmp"];
    cmd.args(safe_args)
}

pub mod local_lookalike {
    pub struct Command;

    impl Command {
        pub fn new(_prog: &str) -> Command {
            Command
        }

        pub fn arg(&mut self, _arg: &str) -> &mut Command {
            self
        }

        pub fn args(&mut self, _args: &[&str]) -> &mut Command {
            self
        }
    }

    pub fn local_command(cmd: &mut Command) -> Command {
        let raw = std::env::var("USER_ARG").unwrap();
        let arg: &str = &raw;
        cmd.arg(arg).args(&[arg]);
        Command::new(arg)
    }
}
