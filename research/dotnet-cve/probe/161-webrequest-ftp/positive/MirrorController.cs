using System.Net;
using Microsoft.AspNetCore.Mvc;

namespace Probe.WebRequestFtp.Positive;

public sealed class MirrorController
{
    // Affected package; the attacker chooses the whole URI, including an ftp: scheme.
    public WebRequest Fetch([FromQuery] string url)
    {
        return WebRequest.Create(url);
    }
}
