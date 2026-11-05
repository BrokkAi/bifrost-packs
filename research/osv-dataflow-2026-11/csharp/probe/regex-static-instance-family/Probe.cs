using System;
using System.Text.RegularExpressions;

namespace Verify.RegexFamily
{
    public sealed class Probe
    {
        public bool Run(string text)
        {
            return Regex.IsMatch(text, Environment.GetEnvironmentVariable("BIFROST_FILTER"));
        }
    }
}
