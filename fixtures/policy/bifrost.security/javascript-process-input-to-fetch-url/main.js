// Inert fixture for bifrost.security.javascript.process-input-to-fetch-url.
// Nothing here runs; the functions only give the analyzer call shapes.

// Positive: the argument is the whole URL.
function download() {
  const target = process.argv[2];
  return fetch(target);
}

// Positive: the argument completes a URL that is sent with options.
function lookup() {
  const host = process.argv[2];
  return fetch("http://" + host + "/status", { method: "GET" });
}

// Positive: the argument is interpolated as the host of the URL.
function mirror() {
  const host = process.argv[2];
  return fetch(`https://${host}/index.json`);
}

// Near miss: the argument is only the request body; the URL is fixed.
function upload() {
  const note = process.argv[2];
  return fetch("https://api.example.test/notes", { method: "POST", body: note });
}

// Near miss: the argument only selects which fixed URL is fetched.
function health() {
  const mode = process.argv[2];
  return mode === "staging" ? fetch("https://staging.example.test/health") : null;
}

module.exports = { download, lookup, mirror, upload, health };
