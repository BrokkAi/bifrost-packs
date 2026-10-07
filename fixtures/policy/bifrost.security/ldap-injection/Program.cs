using System;
using System.DirectoryServices;

namespace Verify.Ldap
{
    public sealed class Probe
    {
        public void Run()
        {
            new DirectorySearcher(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED"));
            new DirectorySearcher("(objectClass=user)");
            new Other.DirectorySearcher("fixed");
        }
    }
}

namespace Other
{
    public sealed class DirectorySearcher
    {
        public DirectorySearcher(string filter) { }
    }
}
