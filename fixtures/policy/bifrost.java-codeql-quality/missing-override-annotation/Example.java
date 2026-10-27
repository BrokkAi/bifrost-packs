// Copyright (c) 2026 Brokk, Inc. SPDX-License-Identifier: Apache-2.0
class Delivery {
    String status() { return "pending"; }
    String status(int attempts) { return "retried"; }
    private void record() {}
    static void reset() {}
}
class ExpressDelivery extends Delivery {
    String status() { return "in transit"; } // Positive: superclass override.
    @Override String status(int attempts) { return "scheduled"; } // Near miss: annotated.
    void record() {} // Near miss: private superclass method is not overridden.
    static void reset() {} // Near miss: static method hiding.
    String status(String label) { return label; } // Near miss: overload.
    Runnable callback() { return () -> {}; } // Near miss: functional expression.
    java.util.function.Supplier<String> reader() { return this::status; } // Method reference.
    static { reset(); } // Near miss: generated class initializer is not a method.
}
enum DeliveryMode { STANDARD, EXPRESS } // Generated enum methods are not source methods.

interface Shape {
    default int area() { return 0; }
    int perimeter();
}
class Square implements Shape {
    public int area() { return 16; } // Positive: overrides an interface default.
    public int perimeter() { return 16; } // Positive: implements an abstract method.
}
class AnnotatedDelivery extends Delivery {
    @java.lang.Override String status() { return "delivered"; } // Qualified near miss.
}
class JdkTask implements Runnable, Comparable<JdkTask> {
    public void run() {} // CodeQL positive; held for engine issue #7179.
    public int compareTo(JdkTask other) { return 0; } // CodeQL positive; #7179.
    public String toString() { return "task"; } // CodeQL positive; #7179.
    public boolean equals(Object other) { return this == other; } // CodeQL positive; #7179.
    @Override public int hashCode() { return 7; } // Annotated JDK near miss.
}
class AuditedDelivery extends Delivery implements Runnable {
    String status() { return "audited"; } // Positive: established edge in a family with an unread JDK ancestor.
    @Override public void run() {}
}
class RetriedDelivery extends Delivery {
    String status() { return "retrying"; } // Positive: first overload.
    String status(int attempts) { return "again"; } // CodeQL positive; second overload, missed until engine issue #7505.
}
