// Incomplete: runInThisContext has no summary, because the code can write to
// the global object. The finding is possible.
const vm = require("vm");

function evaluateHere() {
  const script = process.argv[3];
  return vm.runInThisContext(script);
}

module.exports = { evaluateHere };
