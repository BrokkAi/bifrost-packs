// Incomplete: runInNewContext(code, contextObject) has no summary, because the
// code can write to the caller's context object. The finding is possible.
const vm = require("vm");

function evaluateWithLimits() {
  const expression = process.argv[2];
  return vm.runInNewContext("limit + " + expression, { limit: 10 });
}

module.exports = { evaluateWithLimits };
