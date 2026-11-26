// Incomplete: the finding is reported, but awaiting the promise and reading
// the body go through calls with no summary, so the run is inconclusive.
async function readRemote() {
  const target = process.argv[2];
  const response = await fetch(target);
  return response.text();
}

module.exports = { readRemote };
