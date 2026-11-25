using System;
using System.Text.RegularExpressions;

namespace Verify.RegexPattern.Incomplete
{
    public sealed class TypedLocal
    {
        public bool Run(string text)
        {
            string pattern = Console.ReadLine();
            return Regex.IsMatch(text, pattern);
        }
    }
}
