using System;
using System.Diagnostics;

namespace Probe.ShellInterpreter
{
    // The value reaches the command-language operand of a proven interpreter.
    public sealed class Shell
    {
        public void CmdThroughStart()
        {
            Process.Start("cmd.exe", "/c " + Console.ReadLine());
        }

        public ProcessStartInfo CmdThroughConstructor()
        {
            return new ProcessStartInfo("cmd.exe", "/c " + Console.ReadLine());
        }

        public ProcessStartInfo PosixShellArgumentList()
        {
            var info = new ProcessStartInfo("/bin/sh");
            info.ArgumentList.Add("-c");
            info.ArgumentList.Add(Console.ReadLine());
            return info;
        }

        public ProcessStartInfo ShellExecuteDocument()
        {
            var info = new ProcessStartInfo(Console.ReadLine());
            info.UseShellExecute = true;
            return info;
        }
    }
}
