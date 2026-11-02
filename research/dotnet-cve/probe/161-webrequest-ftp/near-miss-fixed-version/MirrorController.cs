using System.Net;
using Microsoft.AspNetCore.Mvc;

namespace Probe.WebRequestFtp.FixedVersion;

public sealed class MirrorController
{
    // Same flow, but the project locks the fixed 7.0.14 package.
    public WebRequest Fetch([FromQuery] string url)
    {
        return WebRequest.Create(url);
    }
}
