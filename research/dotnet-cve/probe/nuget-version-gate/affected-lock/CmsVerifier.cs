using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.AffectedLock;

public sealed class CmsVerifier
{
    // Locked to 9.0.20, inside [9.0.0, 9.0.21).
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
