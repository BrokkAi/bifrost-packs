using System.Net;
using Microsoft.AspNetCore.Mvc;

namespace Probe.WebRequestFtp.Unknown;

public sealed class MirrorController
{
    // No package reference: System.Net.Requests comes from the net7.0 shared framework, whose patch level is not in the workspace.
    public WebRequest Fetch([FromQuery] string url)
    {
        return WebRequest.Create(url);
    }
}
