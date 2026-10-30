using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace Probe.StartOverloads
{
    public sealed class Launcher
    {
        public void FileName()
        {
            Process.Start(Environment.GetEnvironmentVariable("BUILD_TOOL"));
        }

        public void FileNameAndArguments()
        {
            Process.Start(Environment.GetEnvironmentVariable("BUILD_TOOL"), "--version");
        }

        public void FileNameAndArgumentList(IEnumerable<string> arguments)
        {
            Process.Start(Environment.GetEnvironmentVariable("BUILD_TOOL"), arguments);
        }

        public void LiteralTool()
        {
            Process.Start("notepad.exe");
        }

        public void StartInfo(ProcessStartInfo info)
        {
            Process.Start(info);
        }
    }
}
