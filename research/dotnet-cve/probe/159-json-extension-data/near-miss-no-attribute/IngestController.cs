using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Mvc;

namespace Probe.ExtensionData.NoAttribute;

public sealed class Payload
{
    public string Name { get; set; }

    public Dictionary<string, JsonElement> Extra { get; set; }
}

public sealed class IngestController
{
    // Same model without the attribute.
    public string Ingest([FromBody] Payload payload) => payload.Name;
}
