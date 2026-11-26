// Incomplete: process.argv[2] passed directly as the call argument binds no
// source (bifrost-dev#9986). The whole run fails and is never clean; in a
// workspace with other findings it drops them too, so this case runs alone.
function fetchInline() {
  return fetch(process.argv[2]);
}

module.exports = { fetchInline };
