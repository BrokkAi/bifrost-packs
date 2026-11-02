using System;
using System.Net;
using Microsoft.AspNetCore.Mvc;

namespace Probe.WebRequestFtp.SchemeAllowlist;

public sealed class MirrorController
{
    // http(s)-only allowlist enforced before creation.
    public WebRequest Fetch([FromQuery] string url)
    {
        Uri target = new Uri(url);
        if (target.Scheme != Uri.UriSchemeHttps && target.Scheme != Uri.UriSchemeHttp)
        {
            throw new ArgumentException("scheme");
        }
        return WebRequest.Create(target);
    }
}
