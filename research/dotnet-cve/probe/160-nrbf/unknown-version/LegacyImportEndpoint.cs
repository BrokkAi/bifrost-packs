using System.Formats.Nrbf;
using Microsoft.AspNetCore.Http;

namespace Probe.Nrbf.Unknown;

public sealed class LegacyImportEndpoint
{
    // No package reference and no lock: the effective System.Formats.Nrbf comes
    // from the shared framework, whose exact version is not in the workspace.
    public SerializationRecord Import(IFormFile upload)
    {
        return NrbfDecoder.Decode(upload.OpenReadStream());
    }
}
