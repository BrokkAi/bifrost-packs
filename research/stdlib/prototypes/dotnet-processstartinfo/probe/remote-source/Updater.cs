using System.Diagnostics;
using System.Net.Http;
using System.Threading.Tasks;

namespace Probe.RemoteSource
{
    // A server response selects the executable: the trust boundary the
    // candidate needs.
    public sealed class Updater
    {
        public async Task<ProcessStartInfo> Awaited(HttpContent content)
        {
            var tool = await content.ReadAsStringAsync();
            return new ProcessStartInfo(tool);
        }

        public ProcessStartInfo Blocking(HttpContent content)
        {
            var tool = content.ReadAsStringAsync().Result;
            return new ProcessStartInfo(tool);
        }
    }
}
