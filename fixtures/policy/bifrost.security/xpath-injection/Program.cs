using System;
using System.Xml.XPath;

namespace Verify.XPath
{
    public sealed class Probe
    {
        public void Run(XPathNavigator navigator)
        {
            navigator.Select(Environment.GetEnvironmentVariable("BIFROST_UNTRUSTED"));
            navigator.Select("//fixed");
            Other.XPathNavigator.Select(navigator, "fixed");
        }
    }
}

namespace Other
{
    public static class XPathNavigator
    {
        public static void Select(System.Xml.XPath.XPathNavigator navigator, string expression) { }
    }
}
