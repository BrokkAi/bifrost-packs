// Inert fixture for bifrost.security.javascript.process-input-to-legacy-url-parse.
// Nothing here runs; the functions only give the analyzer call shapes.
const url = require("url");

// Positive: the argument is parsed by the legacy parser.
function parseArgument() {
  const target = process.argv[2];
  return url.parse(target);
}

// Positive: url.format passes a string argument to url.parse.
function formatArgument() {
  const target = process.argv[2];
  return url.format(target);
}

// Positive: parsed, then formatted again (two findings).
function reformatArgument() {
  const target = process.argv[2];
  const parts = url.parse(target);
  return url.format(parts);
}

// Near miss: a constant URL.
function parseConstant() {
  return url.parse("https://example.com/status");
}

// Near miss: the argument is read but only labels a constant URL.
function argumentAsLabel() {
  const target = process.argv[2];
  const label = "run:" + target;
  const status = url.format("https://example.com/");
  return [status, label];
}

// Near miss: the WHATWG URL API, the documented replacement.
function parseWhatwg() {
  const target = process.argv[2];
  return new URL(target);
}

module.exports = {
  parseArgument,
  formatArgument,
  reformatArgument,
  parseConstant,
  argumentAsLabel,
  parseWhatwg,
};
