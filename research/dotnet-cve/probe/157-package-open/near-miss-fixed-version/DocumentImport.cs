using System.IO;
using System.IO.Packaging;
using System.Linq;
using Microsoft.AspNetCore.Http;

namespace Probe.Packaging.FixedVersion;

public sealed class DocumentImport
{
    // Same flow, but the project locks the fixed 8.0.1 package.
    public int CountParts(IFormFile upload)
    {
        using Package package = Package.Open(upload.OpenReadStream(), FileMode.Open);
        return package.GetParts().Count();
    }
}
