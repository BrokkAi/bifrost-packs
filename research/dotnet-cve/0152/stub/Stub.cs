// Fixture stand-in for a NuGet package assembly. Bifrost 0.15.2 needs the
// restored assembly on disk, with at least one public type, before it treats
// the package as activation evidence. The reviewed model supplies the real API.
namespace BifrostFixtureStub
{
    public static class Marker
    {
    }
}
