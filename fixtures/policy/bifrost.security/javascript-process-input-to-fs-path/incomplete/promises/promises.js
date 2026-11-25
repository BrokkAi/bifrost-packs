// Incomplete: fs/promises unlink binds as a sink but has no summary.
const fsp = require("fs/promises");

function removeLater() {
  const target = process.argv[2];
  return fsp.unlink(target);
}

module.exports = { removeLater };
