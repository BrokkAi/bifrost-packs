// Inert fixture for bifrost.security.javascript.process-input-to-vm-code.
// Nothing here runs; the functions only give the analyzer call shapes.
const vm = require("vm");

// Positive: the argument is evaluated in a fresh context.
function evaluateExpression() {
  const expression = process.argv[2];
  return vm.runInNewContext(expression);
}

// Positive: a string built from the argument is evaluated.
function evaluateFormula() {
  const term = process.argv[2];
  return vm.runInNewContext("10 + " + term);
}

// Near miss: the argument only selects which constant expression runs.
function evaluateFixedFormula() {
  const mode = process.argv[2];
  return mode === "double" ? vm.runInNewContext("21 * 2") : 0;
}

module.exports = { evaluateExpression, evaluateFormula, evaluateFixedFormula };
