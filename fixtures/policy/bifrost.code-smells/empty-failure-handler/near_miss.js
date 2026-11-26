export function cancel(body) {
  try {
    body.cancel();
  } catch (e) {
    // Ignored: the cancellation has already been requested.
  }
}

export function eslint(task) {
  try {
    task();
  } catch (e) {
    /* noop */
  }
}

export function named(task) {
  try {
    task();
  } catch (ignored) {}
}

export function underscore(task) {
  try {
    task();
  } catch (_) {}
}
