using System;
using System.Diagnostics;

namespace Probe.ArgumentList
{
    // Near miss: a fixed executable receives the untrusted value as one
    // ArgumentList item, with no shell.
    public sealed class Converter
    {
        private const string Tool = "/usr/bin/convert";

        public ProcessStartInfo AddItem()
        {
            var info = new ProcessStartInfo(Tool);
            info.UseShellExecute = false;
            info.ArgumentList.Add(Console.ReadLine());
            return info;
        }

        public ProcessStartInfo CollectionInitializer()
        {
            return new ProcessStartInfo(Tool) { ArgumentList = { Console.ReadLine() } };
        }
    }
}
