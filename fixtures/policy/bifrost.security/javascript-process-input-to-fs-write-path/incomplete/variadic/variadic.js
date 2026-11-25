// Incomplete: a three-segment path.join. The path model covers only the
// two-argument form, because summaries cannot yet reference a variadic tail.
const fs = require("fs");
const path = require("path");

function writeNested() {
  const name = process.argv[2];
  fs.writeFileSync(path.join("/srv", "uploads", name), "report");
}

module.exports = { writeNested };
