// Incomplete: the callback form of readFile binds as a sink but has no summary.
const fs = require("fs");

function readLater(done) {
  const target = process.argv[2];
  fs.readFile(target, "utf8", done);
}

module.exports = { readLater };
