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
