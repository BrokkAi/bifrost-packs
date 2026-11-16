using Microsoft.AspNetCore.Builder;

namespace BlazorHost.Server
{
    public static class Pipeline
    {
        public static void Configure(WebApplication app)
        {
            app.UseWebAssemblyDebugging();
        }
    }
}
