package demo;

final class FinalType {}
class OpenType {}
class Box<T> {}

class Direct<T extends FinalType, U extends OpenType> {}

class Wildcard {
    Box<? extends FinalType> bad;
    Box<? extends OpenType> nearMiss;
}

class JdkBound<T extends String> {}
