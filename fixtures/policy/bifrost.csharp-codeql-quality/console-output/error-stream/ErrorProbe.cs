using System;
using System.IO;

public class Program
{
    public static void Main()
    {
        Console.SetOut(new StringWriter());
        Console.Error.WriteLine("Main may write to the error stream");
    }
}

public class Importer
{
    public void Fail(string reason)
    {
        Console.Error.WriteLine(reason);
    }

    public TextWriter Diagnostics()
    {
        return Console.Error;
    }

    public void NearMissRedirectedOut(string line)
    {
        Console.WriteLine(line);
        Console.Out.Flush();
    }
}
