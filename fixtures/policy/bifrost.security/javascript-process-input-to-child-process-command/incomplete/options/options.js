// Incomplete: execSync with an options argument has no reviewed model.
const childProcess = require("child_process");

function runWithOptions() {
  const command = process.argv[2];
  return childProcess.execSync(command, { encoding: "utf8" });
}

module.exports = { runWithOptions };
