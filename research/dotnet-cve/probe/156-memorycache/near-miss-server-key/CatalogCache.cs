using Microsoft.Extensions.Caching.Memory;

namespace Probe.MemoryCache.ServerKey;

public enum Region { North, South }

public sealed class CatalogCache
{
    private readonly IMemoryCache cache;

    public CatalogCache(IMemoryCache cache) { this.cache = cache; }

    // Constant key.
    public string Banner() => cache.GetOrCreate("catalog:banner", entry => "welcome");

    // Key from a closed set: the attacker cannot choose its hash.
    public string ForRegion(Region region) => cache.GetOrCreate(region, entry => region.ToString());
}
