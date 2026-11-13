using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;

namespace BlazorHost.Server
{
    public class Startup
    {
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseWebAssemblyDebugging();
            }
        }

        public static void ConfigureDiagnostics(IApplicationBuilder app)
        {
            app.UseWebAssemblyDebugging();
        }

        public static void ConfigureExplicit(IApplicationBuilder app)
        {
            WebAssemblyNetDebugProxyAppBuilderExtensions.UseWebAssemblyDebugging(app);
        }
    }
}
