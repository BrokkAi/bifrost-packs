using System;
using System.Diagnostics;

namespace Probe.PropertyWrites
{
    public sealed class Launcher
    {
        public void Parameter(ProcessStartInfo info)
        {
            info.FileName = Console.ReadLine();
        }

        public ProcessStartInfo Local()
        {
            ProcessStartInfo info = new ProcessStartInfo();
            info.FileName = Console.ReadLine();
            return info;
        }

        public ProcessStartInfo Initializer()
        {
            return new ProcessStartInfo { FileName = Console.ReadLine() };
        }

        public void Constant(ProcessStartInfo info)
        {
            info.FileName = "git";
        }
    }
}
