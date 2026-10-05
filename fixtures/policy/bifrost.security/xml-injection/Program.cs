using System;
using System.Security;
using System.Xml;

namespace Verify.Xml
{
    public sealed class Probe
    {
        public void Run(XmlWriter writer)
        {
            writer.WriteRaw(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED"));
            writer.WriteRaw(SecurityElement.Escape(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED")));
            writer.WriteRaw("<fixed />");
            Other.XmlWriter.WriteRaw(writer, "fixed");
        }
    }
}

namespace Other
{
    public static class XmlWriter
    {
        public static void WriteRaw(System.Xml.XmlWriter writer, string text) { }
    }
}
