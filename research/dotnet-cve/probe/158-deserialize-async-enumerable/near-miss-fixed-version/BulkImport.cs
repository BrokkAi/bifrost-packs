using System.Collections.Generic;
using System.Text.Json;
using Microsoft.AspNetCore.Http;

namespace Probe.Json.FixedVersion;

public sealed class Item { public string Name { get; set; } }

public sealed class BulkImport
{
    // Same flow, but the project locks the fixed 8.0.4 package.
    public IAsyncEnumerable<Item> Read(HttpRequest request)
    {
        return JsonSerializer.DeserializeAsyncEnumerable<Item>(request.Body);
    }
}
