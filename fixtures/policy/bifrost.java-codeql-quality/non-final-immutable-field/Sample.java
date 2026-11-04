package sample;

public class Sample {
    String positive = "initialized";
    final String finalField = "stable";
    String reassigned = "initial";
    Object mutableType = new Object();

    public Sample() {
        positive = "constructor";
    }

    void changeLater() {
        reassigned = "later";
    }
}
