// Incomplete: the finding is reported, but Buffer#toString on the result has
// no summary, so the run stays inconclusive.
const fs = require("fs");
const zlib = require("zlib");

function unpackText(file) {
  const compressed = fs.readFileSync(file);
  const out = zlib.brotliDecompressSync(compressed);
  return out.toString("utf8");
}

module.exports = { unpackText };
