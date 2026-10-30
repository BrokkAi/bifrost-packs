using System;
using System.Diagnostics;

namespace Probe.CtorFileName
{
    // Binding witness. Environment and console input are caller-controlled,
    // so these flows show that the sink binds; they are not security findings.
    public sealed class ToolLauncher
    {
        private const string Converter = "/usr/bin/convert";

        public ProcessStartInfo FromEnvironment()
        {
            return new ProcessStartInfo(Environment.GetEnvironmentVariable("BUILD_TOOL"));
        }

        public ProcessStartInfo FromImplicitLocal()
        {
            var tool = Console.ReadLine();
            return new ProcessStartInfo(tool);
        }

        public ProcessStartInfo ThroughHelper()
        {
            return Describe(Console.ReadLine());
        }

        private static ProcessStartInfo Describe(string executable)
        {
            return new ProcessStartInfo(executable);
        }

        public ProcessStartInfo LiteralTool()
        {
            return new ProcessStartInfo("git");
        }

        public ProcessStartInfo ConstantTool()
        {
            return new ProcessStartInfo(Converter);
        }

        public void SameNamedLocalType()
        {
            Local.Tools.ProcessStartInfo info = new Local.Tools.ProcessStartInfo(Console.ReadLine());
        }
    }
}

namespace Local.Tools
{
    public sealed class ProcessStartInfo
    {
        public ProcessStartInfo(string fileName) { }
    }
}
