export function context(read: () => unknown): unknown {
  let value: unknown
  try {
    value = read()
  } catch {
    // Do nothing: an absent execution context is allowed.
  }
  return value
}

export function expected(task: () => void): void {
  try {
    task()
  } catch (expected) {}
}
