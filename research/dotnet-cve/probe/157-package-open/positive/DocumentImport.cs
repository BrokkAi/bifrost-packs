using System.IO;
using System.IO.Packaging;
using System.Linq;
using Microsoft.AspNetCore.Http;

namespace Probe.Packaging.Positive;

public sealed class DocumentImport
{
    // Affected package; an uploaded .docx stream is opened as a package.
    public int CountParts(IFormFile upload)
    {
        using Package package = Package.Open(upload.OpenReadStream(), FileMode.Open);
        return package.GetParts().Count();
    }
}
