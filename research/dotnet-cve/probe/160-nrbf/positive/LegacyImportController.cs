using System.Formats.Nrbf;
using Microsoft.AspNetCore.Http;

namespace Probe.Nrbf.Positive;

public sealed class LegacyImportController
{
    // Affected prerelease package; uploaded legacy BinaryFormatter bytes are decoded.
    public SerializationRecord Import(IFormFile upload)
    {
        return NrbfDecoder.Decode(upload.OpenReadStream());
    }
}
