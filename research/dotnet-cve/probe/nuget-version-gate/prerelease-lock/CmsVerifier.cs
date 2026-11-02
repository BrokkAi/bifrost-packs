using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.PrereleaseLock;

public sealed class CmsVerifier
{
    // Locked to 11.0.0-rc.1, below the fixed 11.0.0-rc.2.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
