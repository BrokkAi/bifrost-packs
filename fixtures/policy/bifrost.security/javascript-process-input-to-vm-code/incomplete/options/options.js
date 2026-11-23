// Incomplete: runInThisContext with an options argument has no reviewed model,
// and its result is used.
const vm = require("vm");

function evaluateNamed() {
  const script = process.argv[2];
  const result = vm.runInThisContext(script, { filename: "user.js" });
  return vm.runInNewContext("String(value)", { value: result });
}

module.exports = { evaluateNamed };
