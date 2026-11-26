class Positive {
  void run(Runnable task) {
    try {
      task.run();
    } catch (RuntimeException e) {
    }
  }

  void unfinished(Runnable task) {
    try {
      task.run();
    } catch (RuntimeException e) {
      // FIXME: propagate
    }
  }

  void ignoredButUnfinished(Runnable task) {
    try {
      task.run();
    } catch (RuntimeException ignored) {
      // TODO: decide whether this can really be ignored
    }
  }
}
