using System.IO;
using System.IO.Packaging;

namespace Probe.Packaging.SelfCreated;

public sealed class ReportWriter
{
    // The application creates and reopens its own package in memory.
    public Package Create(MemoryStream buffer)
    {
        return Package.Open(buffer, FileMode.Create);
    }
}
