using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;

namespace Probe.ExtensionData.Generic;

public sealed class Extras
{
    [JsonExtensionData] public Dictionary<string, JsonElement> Values { get; set; }
}

public sealed class Envelope<T>
{
    public T Body { get; set; }
}

public sealed class IngestController
{
    // The attribute is reachable only through the closed generic Envelope<Extras>.
    public int Ingest([FromBody] Envelope<Extras> envelope) => envelope.Body.Values.Count;
}
