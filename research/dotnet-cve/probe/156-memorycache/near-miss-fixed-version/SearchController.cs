using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;

namespace Probe.MemoryCache.FixedVersion;

public sealed class SearchController
{
    private readonly IMemoryCache cache;

    public SearchController(IMemoryCache cache) { this.cache = cache; }

    // Same flow, but the project locks the fixed 8.0.1 package.
    public string Search([FromQuery] string q)
    {
        return cache.GetOrCreate(q, entry => Lookup(q));
    }

    private static string Lookup(string term) => term.ToUpperInvariant();
}
