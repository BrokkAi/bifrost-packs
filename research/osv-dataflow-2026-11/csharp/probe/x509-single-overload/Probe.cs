using System;
using System.Security.Cryptography.X509Certificates;
namespace V
{
    public sealed class Probe
    {
        public X509Certificate2 FromPath()
        {
            return new X509Certificate2(Environment.GetEnvironmentVariable("CLIENT_CERT_PATH"));
        }
    }
}
