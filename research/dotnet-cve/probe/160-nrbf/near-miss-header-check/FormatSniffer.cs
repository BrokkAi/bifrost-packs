using System.Formats.Nrbf;
using Microsoft.AspNetCore.Http;

namespace Probe.Nrbf.Header;

public sealed class FormatSniffer
{
    // Only the header check runs on the upload; nothing is decoded.
    public bool IsLegacyPayload(IFormFile upload)
    {
        return NrbfDecoder.StartsWithPayloadHeader(upload.OpenReadStream());
    }
}
