using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;

namespace Probe.MemoryCache.Unknown;

public sealed class SessionStore
{
    private readonly IMemoryCache cache;

    public SessionStore(IMemoryCache cache) { this.cache = cache; }

    // Extension-method form on the interface plus the interface's own
    // TryGetValue; neither call resolves on Bifrost 0.14.2.
    public bool Touch([FromHeader] string token)
    {
        cache.Set(token, true);
        return cache.TryGetValue(token, out _);
    }
}
