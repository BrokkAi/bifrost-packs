using DocumentFormat.OpenXml.Packaging;
using Microsoft.AspNetCore.Http;

namespace Probe.Packaging.Transitive;

public sealed class WordImport
{
    // System.IO.Packaging arrives transitively through the OpenXML SDK.
    // The call site belongs to the SDK; the packaging copy is a dependency
    // fact, not a call-site finding, and the SDK is not modeled here.
    public string Title(IFormFile upload)
    {
        using WordprocessingDocument document = WordprocessingDocument.Open(upload.OpenReadStream(), false);
        return document.PackageProperties.Title;
    }
}
