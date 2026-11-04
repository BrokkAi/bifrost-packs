using System;
using System.IO;
using System.Reflection;

namespace Verify.AssemblyPath
{
    public sealed class Probe
    {
        public void Run()
        {
            Assembly.LoadFrom(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED"));
            Assembly.LoadFrom(Path.GetFileName(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED")));
            Assembly.LoadFrom("built-in.dll");
            Other.Assembly.LoadFrom("fixed");
        }
    }
}

namespace Other
{
    public static class Assembly
    {
        public static void LoadFrom(string path) { }
    }
}
