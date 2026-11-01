using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.FrameworkExplicit;

public sealed class CmsVerifier
{
    // Explicit FrameworkReference: the runtime picks the version.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
