using System.Formats.Nrbf;
using System.IO;

namespace Probe.Nrbf.Trusted;

public sealed class SnapshotLoader
{
    // Bytes the application wrote itself to its own data directory.
    public SerializationRecord Load()
    {
        return NrbfDecoder.Decode(File.OpenRead("data/snapshot.bin"));
    }
}
