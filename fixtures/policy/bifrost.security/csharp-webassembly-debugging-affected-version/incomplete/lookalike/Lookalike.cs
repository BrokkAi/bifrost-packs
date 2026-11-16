namespace BlazorHost.Server
{
    // An application type with a method of the same name. Its calls bind to
    // this workspace declaration, not to the WebAssembly.Server package.
    public sealed class DebugSwitches
    {
        public bool Enabled { get; private set; }

        public void UseWebAssemblyDebugging()
        {
            Enabled = true;
        }
    }

    public static class Lookalike
    {
        public static DebugSwitches Configure(DebugSwitches switches)
        {
            switches.UseWebAssemblyDebugging();
            return switches;
        }
    }
}
