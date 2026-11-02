using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.NoLock;

public sealed class CmsVerifier
{
    // PackageReference floor 9.0.20 with no lock or restore output: version unknown.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
