using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Probe.ExtensionData.Newtonsoft;

public sealed class Payload
{
    public string Name { get; set; }

    // Same attribute name, but Newtonsoft.Json's own type: not System.Text.Json.
    [JsonExtensionData] public IDictionary<string, JToken> Extra { get; set; }
}

public sealed class IngestController
{
    public string Ingest([FromBody] Payload payload) => payload.Name;
}
