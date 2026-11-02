using System.Collections.Generic;
using System.Text.Json;
using Microsoft.AspNetCore.Http;

namespace Probe.Json.Unknown;

public sealed class Item { public string Name { get; set; } }

public sealed class BulkImport
{
    // No package reference: System.Text.Json comes from the net8.0 shared framework, whose patch level is not in the workspace.
    public IAsyncEnumerable<Item> Read(HttpRequest request)
    {
        return JsonSerializer.DeserializeAsyncEnumerable<Item>(request.Body);
    }
}
