using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;

namespace Probe.ExtensionData.Positive;

public sealed class Payload
{
    public string Name { get; set; }

    [JsonExtensionData] public Dictionary<string, JsonElement> Extra { get; set; }
}

public sealed class IngestController
{
    // Affected package; MVC binds the request body into a model with [JsonExtensionData].
    public string Ingest([FromBody] Payload payload) => payload.Name;
}
