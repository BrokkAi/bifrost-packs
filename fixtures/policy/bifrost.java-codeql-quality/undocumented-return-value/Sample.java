package sample;

import java.io.IOException;

public class Sample {
    public static class PositiveType {}

    /** Documented type. */
    public static class DocumentedType {}

    private static class PrivateType {}

    public void undocumentedFunction() {}

    /** Documented method. */
    public void documentedFunction() {}

    /** Missing parameter tag. */
    public void undocumentedParameter(String value) {}

    /** @param value documented */
    public void documentedParameter(String value) {}

    /** @param wrong no such parameter */
    public void unknownParameter(String actual) {}

    /** @param actual correct */
    public void knownParameter(String actual) {}

    /** Missing return tag. */
    public String undocumentedReturn() { return "value"; }

    /** @return documented */
    public String documentedReturn() { return "value"; }

    /** Missing throws tag. */
    public void undocumentedException() throws IOException {}

    /** @throws IOException documented */
    public void documentedException() throws IOException {}

    /** @throws IOException impossible here */
    public void inconsistentThrows() {}

    /** @throws RuntimeException unchecked */
    public void uncheckedThrows() {}

    public String getValue() { return "value"; }

    public void setValue(String value) {}
}
