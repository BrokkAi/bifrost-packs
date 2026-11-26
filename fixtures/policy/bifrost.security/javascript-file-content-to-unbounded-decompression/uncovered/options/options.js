// Known false negative: the options object omits maxOutputLength, so the
// output is still unbounded. The call binds to the two-argument member,
// which is not a sink, and nothing is reported.
const fs = require("fs");
const zlib = require("zlib");

function unpackWithOptions(file) {
  const data = fs.readFileSync(file);
  return zlib.gunzipSync(data, { finishFlush: zlib.constants.Z_SYNC_FLUSH });
}

module.exports = { unpackWithOptions };
