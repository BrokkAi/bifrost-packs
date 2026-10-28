using System;
using System.Diagnostics;
using System.IO;

public class Program
{
    public static int Main(string[] args)
    {
        Console.WriteLine("starting {0}", args.Length);
        Console.Out.Flush();
        Action report = () => Console.WriteLine("done");
        report();
        return 0;
    }
}

public class OrderService
{
    public void Place(string id, decimal total)
    {
        Console.WriteLine("placing {0} for {1}", id, total);
        Console.Write('.');
        System.Console.WriteLine(id);
        global::System.Console.Write(total);
    }

    public TextWriter Sink()
    {
        return Console.Out;
    }

    public void Main()
    {
        Console.WriteLine("instance Main is not an entry point");
    }

    public static void Main(string first, string second)
    {
        Console.WriteLine(first + second);
    }

    public void NearMissWriter(TextWriter writer, string id)
    {
        writer.WriteLine(id);
        Debug.WriteLine(id);
        Trace.Write(id);
    }

    public string NearMissRead()
    {
        return Console.ReadLine();
    }

    public void NearMissErrorRedirected(string id)
    {
        Console.Error.WriteLine(id);
    }
}
