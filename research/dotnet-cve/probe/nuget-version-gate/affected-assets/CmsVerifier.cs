using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.AffectedAssets;

public sealed class CmsVerifier
{
    // Restored 8.0.1, inside [8.0.0, 8.0.2); no lock file.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
