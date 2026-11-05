package env;
public class Main {
    public static void run() throws Exception {
        String cmd = System.getenv("CMD");
        Runtime.getRuntime().exec(cmd);
    }
}
