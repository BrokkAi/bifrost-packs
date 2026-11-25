// Not covered: execFile is not a sink of this rule, and no shell runs the
// argument unless the shell option is set.
const childProcess = require("child_process");

function runTool() {
  const file = process.argv[2];
  childProcess.execFile("/usr/bin/file", [file]);
}

module.exports = { runTool };
