// Inert fixture for bifrost.security.javascript.process-input-to-child-process-command.
// Nothing here runs; the functions only give the analyzer call shapes.
const childProcess = require("child_process");

// Positive: the argument is the whole command.
function runNamedCommand() {
  const command = process.argv[2];
  return childProcess.execSync(command);
}

// Positive: the argument is concatenated into a shell command line.
function listDirectory() {
  const dir = process.argv[2];
  return childProcess.execSync("ls -l " + dir);
}

// Positive: a template literal builds the command line.
function archive() {
  const name = process.argv[3];
  return childProcess.execSync(`tar czf /tmp/backup.tgz ${name}`);
}

// Near miss: a constant command; the argument is only compared.
function status() {
  const verbose = process.argv[2];
  return verbose === "-v" ? childProcess.execSync("git status") : "";
}

module.exports = { runNamedCommand, listDirectory, archive, status };
