const fs = require("fs");
let path = "/tmp/reassigned";

if (!fs.existsSync(path)) {
  path = "/tmp/other";
  fs.writeFileSync(path, "data");
}
