using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;

namespace Probe.ExtensionData.FixedVersion;

public sealed class Payload
{
    public string Name { get; set; }

    [JsonExtensionData] public Dictionary<string, JsonElement> Extra { get; set; }
}

public sealed class IngestController
{
    // Same model, but the project locks the fixed 8.0.5 package.
    public string Ingest([FromBody] Payload payload) => payload.Name;
}
