const fs = require("fs");
const checkedPath = "/tmp/checked";

if (!fs.existsSync(checkedPath)) {
  fs.writeFileSync(checkedPath, "data");
}

const unrelatedPath = "/tmp/unrelated";
fs.writeFileSync(unrelatedPath, "data");

if (!fs.existsSync("/tmp/literal")) {
  fs.writeFileSync("/tmp/literal", "data");
}

if (fs.existsSync(checkedPath)) {
  fs.readFileSync(checkedPath);
}

// Keep the fixture content identity distinct from pre-decoded structural facts.
