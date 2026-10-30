using System;
using System.Net;
using Microsoft.AspNetCore.Mvc;

namespace Probe.WebRequestFtp.ConstantBase;

public sealed class MirrorController
{
    private static readonly Uri Base = new Uri("https://mirror.example.com/files/");

    // Constant https base; only a validated, escaped path segment varies.
    public WebRequest Fetch([FromQuery] string name)
    {
        if (!Guid.TryParse(name, out Guid id))
        {
            throw new ArgumentException("name");
        }
        return WebRequest.Create(new Uri(Base, Uri.EscapeDataString(id.ToString())));
    }
}
