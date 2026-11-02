using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.FixedLock;

public sealed class CmsVerifier
{
    // Locked to the fixed 9.0.21.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
