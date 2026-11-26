// Incomplete: a require inside the function body does not resolve to the
// declared zlib module, so the sink does not bind. The run fails and is
// never clean.
const fs = require("fs");

function unpackLazily(file) {
  const zlib = require("zlib");
  return zlib.gunzipSync(fs.readFileSync(file));
}

module.exports = { unpackLazily };
