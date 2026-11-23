// Incomplete: path.basename has no reviewed summary, so the guard is unmodeled.
const fs = require("fs");
const path = require("path");

function readBasename() {
  const name = path.basename(process.argv[2]);
  return fs.readFileSync(path.join("/srv/reports", name), "utf8");
}

module.exports = { readBasename };
