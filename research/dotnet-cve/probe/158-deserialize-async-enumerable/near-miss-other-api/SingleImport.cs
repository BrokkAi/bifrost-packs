using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;

namespace Probe.Json.OtherApi;

public sealed class Item { public string Name { get; set; } }

public sealed class SingleImport
{
    // DeserializeAsync is a different API, outside the advisory.
    public ValueTask<Item> Read(HttpRequest request)
    {
        return JsonSerializer.DeserializeAsync<Item>(request.Body);
    }
}
