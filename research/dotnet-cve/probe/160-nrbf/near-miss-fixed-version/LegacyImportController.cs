using System.Formats.Nrbf;
using Microsoft.AspNetCore.Http;

namespace Probe.Nrbf.FixedVersion;

public sealed class LegacyImportController
{
    // Same call shape, but the project locks System.Formats.Nrbf 9.0.0.
    public SerializationRecord Import(IFormFile upload)
    {
        return NrbfDecoder.Decode(upload.OpenReadStream());
    }
}
