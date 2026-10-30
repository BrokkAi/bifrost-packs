using System;
using System.Diagnostics;

namespace Probe.TypedLocal
{
    public sealed class TypedLocal
    {
        // Same flow as FromImplicitLocal, but the local is declared `string`.
        public ProcessStartInfo FromTypedLocal()
        {
            string tool = Console.ReadLine();
            return new ProcessStartInfo(tool);
        }
    }
}
