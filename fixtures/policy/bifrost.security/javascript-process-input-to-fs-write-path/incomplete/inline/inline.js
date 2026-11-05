// Incomplete: process.argv[2] passed directly as the call argument. The engine
// leaves source discovery incomplete and reports nothing.
const fs = require("fs");

function writeInline() {
  fs.writeFileSync(process.argv[2], "report");
}

module.exports = { writeInline };
