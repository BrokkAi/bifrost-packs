package _;

class Underscore {
  void run(int _) {
    System.out.println(_);
  }

  void _() {
    int _ = 1;
    System.out.println(_);
  }
}

class Good {
  void run(int value) {
    System.out.println(value);
  }
}

class OnlyDeclaration {
  void _() {}
}

// Legacy underscore method declarations exercise parser recovery.
