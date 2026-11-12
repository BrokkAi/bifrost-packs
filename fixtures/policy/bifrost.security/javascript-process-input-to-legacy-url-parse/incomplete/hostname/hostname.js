// Incomplete: reading .hostname from the parsed result. The Url object has no
// reviewed property model, so access-path resolution is unknown. The finding
// at url.parse is still reported.
const url = require("url");

function allowedHost(allowlist) {
  const target = process.argv[2];
  const host = url.parse(target).hostname;
  return allowlist.includes(host);
}

module.exports = { allowedHost };
