// Incomplete: path.basename has no reviewed summary, so the guard is unmodeled.
const fs = require("fs");
const path = require("path");

function writeBasename() {
  const name = process.argv[2];
  fs.writeFileSync(path.join("/srv/uploads", path.basename(name)), "report");
}

module.exports = { writeBasename };
