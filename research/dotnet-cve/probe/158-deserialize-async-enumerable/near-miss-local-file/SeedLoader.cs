using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace Probe.Json.LocalFile;

public sealed class Item { public string Name { get; set; } }

public sealed class SeedLoader
{
    // A file the application ships with.
    public IAsyncEnumerable<Item> Read()
    {
        return JsonSerializer.DeserializeAsyncEnumerable<Item>(File.OpenRead("seed/items.json"));
    }
}
