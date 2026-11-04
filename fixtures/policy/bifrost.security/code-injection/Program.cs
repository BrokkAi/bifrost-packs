using System;
using System.CodeDom.Compiler;

namespace Verify.Code
{
    public sealed class Probe
    {
        public void Run(CodeDomProvider provider, CompilerParameters options)
        {
            provider.CompileAssemblyFromSource(options, Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED"));
            provider.CompileAssemblyFromSource(options, "return 1;");
            Other.CodeDomProvider.CompileAssemblyFromSource(options, "fixed");
        }
    }
}

namespace Other
{
    public static class CodeDomProvider
    {
        public static void CompileAssemblyFromSource(CompilerParameters options, string source) { }
    }
}
