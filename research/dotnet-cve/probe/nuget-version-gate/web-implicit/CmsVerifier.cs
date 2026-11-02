using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.WebImplicit;

public sealed class CmsVerifier
{
    // Web SDK, not restored: the implicit Microsoft.AspNetCore.App reference.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
