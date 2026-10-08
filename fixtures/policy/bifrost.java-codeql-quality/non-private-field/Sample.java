package sample;

class Holder {
    public int unused = 1;
    private int privateField = 2;
    public static final int constant = 3;
    public int externallyUsed = 4;
}

class Reader {
    int read(Holder holder) {
        return holder.externallyUsed;
    }
}
