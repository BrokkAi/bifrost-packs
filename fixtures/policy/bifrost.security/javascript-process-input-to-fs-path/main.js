// Inert fixture for bifrost.security.javascript.process-input-to-fs-path.
// Nothing here runs; the functions only give the analyzer call shapes.
const fs = require("fs");
const path = require("path");

const REPORT_DIR = "/srv/reports";

// Positive: the argument is read as given.
function readNamedReport() {
  const target = process.argv[2];
  return fs.readFileSync(target, "utf8");
}

// Positive: path.join resolves "../" in the segment, so it escapes REPORT_DIR.
function readUnderReports() {
  const name = process.argv[2];
  return fs.readFileSync(path.join(REPORT_DIR, name));
}

// Positive: listing a caller-chosen directory.
function listDirectory() {
  const dir = process.argv[2];
  return fs.readdirSync(path.resolve(REPORT_DIR, dir));
}

// Positive: probing whether a caller-chosen file exists, and its metadata.
function probe() {
  const raw = process.argv[3];
  const target = path.normalize(raw);
  if (fs.existsSync(target)) {
    return fs.statSync(target);
  }
  return fs.lstatSync(REPORT_DIR);
}

// Positive: checking access to a caller-chosen file.
function checkAccess() {
  const target = process.argv[2];
  fs.accessSync(target, 4);
}

// Positive: removing a caller-chosen file and tree.
function removeReport() {
  const target = process.argv[2];
  fs.unlinkSync(target);
}

function removeTree() {
  const dir = process.argv[2];
  fs.rmSync(path.join(REPORT_DIR, dir), { recursive: true });
}

function removeSingle() {
  const target = process.argv[2];
  fs.rmSync(target);
}

// Near miss: the argument only selects a format, never the path.
function readFixedReport() {
  const format = process.argv[2];
  const body = fs.readFileSync(path.join(REPORT_DIR, "latest.txt"), "utf8");
  return format === "text" ? body : "";
}

// Near miss: file content read from a fixed path is not the path operand.
function listFromIndex() {
  const index = fs.readFileSync(path.join(REPORT_DIR, "index.txt"), "utf8");
  return fs.existsSync(path.join(REPORT_DIR, "ready")) ? index : "";
}

module.exports = {
  readNamedReport,
  readUnderReports,
  listDirectory,
  probe,
  checkAccess,
  removeReport,
  removeTree,
  removeSingle,
  readFixedReport,
  listFromIndex,
};
