export function run(task) {
  try {
    task();
  } catch (e) {}
}

export function probe(task) {
  try {
    task();
  } catch {}
}

export function unfinished(task) {
  try {
    task();
  } catch (e) {
    // TODO: surface this error
  }
}

export function trailing(task) {
  try {
    task();
  } catch {} // a comment after the clause does not count
}
