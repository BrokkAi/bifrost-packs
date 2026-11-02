namespace Local
{
    public static class Console
    {
        public static void WriteLine(string message)
        {
        }
    }

    public class Reporter
    {
        public void NearMissLocalConsole(string message)
        {
            Console.WriteLine(message);
        }
    }
}
