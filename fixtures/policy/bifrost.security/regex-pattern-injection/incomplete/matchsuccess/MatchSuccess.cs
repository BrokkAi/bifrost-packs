using System;
using System.Text.RegularExpressions;

namespace Verify.RegexPattern.Incomplete
{
    public sealed class MatchSuccess
    {
        public bool Run(string text)
        {
            return Regex.Match(text, Console.ReadLine()).Success;
        }
    }
}
