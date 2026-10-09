const fs = require("fs");

if (!fs.existsSync(3)) {
  fs.writeFileSync(3, "data");
}
