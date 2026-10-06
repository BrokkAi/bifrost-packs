package demo;

class Box<T> {}

class Sample {
    Box raw() {
        return new Box();
    }

    Box<String> parameterized() {
        return new Box<String>();
    }
}
