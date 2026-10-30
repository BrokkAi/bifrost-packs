using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace Probe.CtorArguments
{
    public sealed class Launcher
    {
        public ProcessStartInfo WithArguments()
        {
            return new ProcessStartInfo(Environment.GetEnvironmentVariable("BUILD_TOOL"), "--version");
        }

        public ProcessStartInfo WithArgumentList(List<string> arguments)
        {
            return new ProcessStartInfo(Environment.GetEnvironmentVariable("BUILD_TOOL"), arguments);
        }
    }
}
