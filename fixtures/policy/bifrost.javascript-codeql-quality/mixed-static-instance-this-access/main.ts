class InstanceUsesStatic {
  bar() {
    this.baz();
  }

  static baz() {}
}

class StaticUsesInstance {
  static bar() {
    this.baz();
  }

  baz() {}
}

class Consistent {
  static bar() {
    this.baz();
  }

  static baz() {}
}

class InstanceFieldUsesStatic {
  bar() {
    this.value;
  }

  static value = 1;
}

class StaticFieldUsesInstance {
  static bar() {
    this.value;
  }

  value = 1;
}

class ConsistentFields {
  static bar() {
    this.value;
  }

  static value = 1;
}
