// Incomplete: destructured require bindings do not resolve to the declared
// members, so neither the source nor the sink binds. The run fails and is
// never clean.
const { readFileSync } = require("fs");
const { gunzipSync } = require("zlib");

function unpackDestructured(file) {
  return gunzipSync(readFileSync(file));
}

module.exports = { unpackDestructured };
