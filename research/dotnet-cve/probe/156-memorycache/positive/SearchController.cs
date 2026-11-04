using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;

namespace Probe.MemoryCache.Positive;

public sealed class SearchController
{
    private readonly IMemoryCache cache;

    public SearchController(IMemoryCache cache) { this.cache = cache; }

    // Affected package; the request query string is the cache key.
    public string Search([FromQuery] string q)
    {
        return cache.GetOrCreate(q, entry => Lookup(q));
    }

    private static string Lookup(string term) => term.ToUpperInvariant();
}
