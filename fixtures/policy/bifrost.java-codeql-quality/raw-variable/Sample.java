package demo;

class Box<T> {}

class Sample {
    Box raw = null;
    Box<String> parameterized = null;

    void locals(Box parameter, Box<String> parameterizedParameter) {
        Box local = null;
        Box<String> parameterizedLocal = null;
    }
}
