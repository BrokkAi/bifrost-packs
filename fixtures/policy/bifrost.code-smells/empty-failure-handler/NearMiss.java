class NearMiss {
  void comment(Runnable task) {
    try {
      task.run();
    } catch (IllegalArgumentException e) {
      // Not an IP literal; fall through to host name parsing.
    }
  }

  void ignored(Runnable task) {
    try {
      task.run();
    } catch (RuntimeException ignored) {
    }
  }

  void tolerated(Runnable task) {
    try {
      task.run();
    } catch (UnsupportedOperationException tolerated) {
    }
  }

  void expected(Runnable task) {
    try {
      task.run();
    } catch (IllegalStateException expected) {
    }
  }
}
