using System.Collections.Generic;
using System.Text.Json;
using Microsoft.AspNetCore.Http;

namespace Probe.Json.Positive;

public sealed class Item { public string Name { get; set; } }

public sealed class BulkImport
{
    // Affected package; the request body is streamed as a JSON array.
    public IAsyncEnumerable<Item> Read(HttpRequest request)
    {
        return JsonSerializer.DeserializeAsyncEnumerable<Item>(request.Body);
    }
}
