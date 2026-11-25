// Inert fixture for bifrost.security.javascript.process-input-to-fs-write-path.
// Nothing here runs; the functions only give the analyzer call shapes.
const fs = require("fs");
const path = require("path");

const UPLOAD_DIR = "/srv/uploads";

// Positive: the argument is written as given.
function writeNamedFile() {
  const target = process.argv[2];
  fs.writeFileSync(target, "report");
}

// Positive: path.join resolves "../" in the segment, so it escapes UPLOAD_DIR.
function writeUnderUploads() {
  const name = process.argv[2];
  const target = path.join(UPLOAD_DIR, name);
  fs.writeFileSync(target, "report");
}

// Positive: path.join with the argument as the base.
function appendToDirectory() {
  const dir = process.argv[2];
  const logFile = path.join(dir, "audit.log");
  fs.appendFileSync(logFile, "entry\n");
}

// Positive: path.normalize does not confine its input.
function openNormalized() {
  const raw = process.argv[3];
  return fs.openSync(path.normalize(raw), "w");
}

// Positive: path.resolve with an absolute segment ignores the base.
function writeResolved() {
  const name = process.argv[2];
  fs.writeFileSync(path.resolve(UPLOAD_DIR, name), "report");
}

// Near miss: the argument is the written content, not the path.
function argumentAsContent() {
  const note = process.argv[2];
  fs.writeFileSync(path.join(UPLOAD_DIR, "notes.txt"), note);
}

// Near miss: a constant path.
function constantPath() {
  fs.writeFileSync(path.join(UPLOAD_DIR, "status.txt"), "ok");
}

module.exports = {
  writeNamedFile,
  writeUnderUploads,
  appendToDirectory,
  openNormalized,
  writeResolved,
  argumentAsContent,
  constantPath,
};
