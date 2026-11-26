// Inert fixture for bifrost.security.javascript.file-content-to-unbounded-decompression.
// Nothing here runs; the functions only give the analyzer call shapes.
const fs = require("fs");
const zlib = require("zlib");
const nodeZlib = require("node:zlib");

// Positive: a gzip file is expanded with no output limit.
function unpackGzip(file) {
  const data = fs.readFileSync(file);
  return zlib.gunzipSync(data);
}

// Positive: a Brotli file is expanded with no output limit.
function unpackBrotli(file) {
  const compressed = fs.readFileSync(file);
  return zlib.brotliDecompressSync(compressed);
}

// Positive: deflate, raw deflate and auto-detected streams.
function unpackDeflate(file) {
  return zlib.inflateSync(fs.readFileSync(file));
}

function unpackRaw(file) {
  const body = fs.readFileSync(file);
  const copy = body;
  return zlib.inflateRawSync(copy);
}

function unpackAuto(file) {
  return zlib.unzipSync(fs.readFileSync(file));
}

// Positive: the node: scheme names the same module.
function unpackPrefixed(file) {
  return nodeZlib.gunzipSync(fs.readFileSync(file));
}

// Near miss: maxOutputLength bounds the output.
function unpackBounded(file) {
  const data = fs.readFileSync(file);
  return zlib.gunzipSync(data, { maxOutputLength: 1 << 20 });
}

// Near miss: the file content is never decompressed.
function readText(file) {
  const text = fs.readFileSync(file, "utf8");
  return text.length;
}

module.exports = { unpackGzip, unpackBrotli, unpackDeflate, unpackRaw, unpackAuto, unpackPrefixed, unpackBounded, readText };
