package sample;

public class Sample {
    int BadField;
    void run(int BadParam) {
        int BadLocal = BadParam;
        int goodLocal = BadLocal;
    }
}
