using System;
using System.Text.RegularExpressions;

namespace Verify.RegexPattern.Incomplete
{
    public sealed class Field
    {
        private readonly string pattern = Environment.GetEnvironmentVariable("BIFROST_FILTER");

        public bool Run(string text)
        {
            return Regex.IsMatch(text, pattern);
        }
    }
}
