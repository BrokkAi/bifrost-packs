export function run(task: () => void): void {
  try {
    task()
  } catch (e) {}
}

export function probe(task: () => void): void {
  try {
    task()
  } catch {}
}
