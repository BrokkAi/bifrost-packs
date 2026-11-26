// Incomplete: the URL constructor has no model, so the run is inconclusive
// and nothing is reported.
function resolveAndFetch() {
  const path = process.argv[2];
  return fetch(new URL(path, "https://api.example.test/"));
}

module.exports = { resolveAndFetch };
