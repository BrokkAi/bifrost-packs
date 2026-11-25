// Incomplete: the vm.Script constructor binds as a sink but has no summary.
const vm = require("vm");

function compileLater() {
  const source = process.argv[2];
  return new vm.Script(source);
}

module.exports = { compileLater };
