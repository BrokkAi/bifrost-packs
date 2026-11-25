// Incomplete: exec has no reviewed model, and its result is used.
const childProcess = require("child_process");

function runLater() {
  const command = process.argv[2];
  const child = childProcess.exec(command);
  return childProcess.execSync("kill " + child.pid);
}

module.exports = { runLater };
