using System;
using System.Text.RegularExpressions;

namespace Verify.RegexPattern.Incomplete
{
    public sealed class Evaluator
    {
        public string Run(string text)
        {
            return Regex.Replace(text, Console.ReadLine(), m => "*");
        }
    }
}
