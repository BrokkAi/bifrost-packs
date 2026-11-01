using System.Security.Cryptography.Pkcs;

namespace Probe.NugetGate.InboxRuntime;

public sealed class CmsVerifier
{
    // No package reference: SignedCms comes from a framework copy whose version is not in the workspace.
    public void Verify(byte[] envelope)
    {
        SignedCms cms = new SignedCms();
        cms.Decode(envelope);
        cms.CheckSignature(true);
    }
}
