// Uncovered: the callback form zlib.gunzip(buffer, callback) has no
// declaration and is not a sink. Its result is unused, so the run is
// complete and nothing is reported.
const fs = require("fs");
const zlib = require("zlib");

function unpackLater(file, done) {
  const data = fs.readFileSync(file);
  zlib.gunzip(data, done);
}

module.exports = { unpackLater };
