using System;
using System.Text.RegularExpressions;

namespace Verify.RegexPattern
{
    public sealed class Probe
    {
        public bool ConstructorFromEnvironment()
        {
            var filter = new Regex(Environment.GetEnvironmentVariable("BIFROST_FILTER"));
            return filter != null;
        }

        public bool ConstructorWithOptions()
        {
            var filter = new Regex(Console.ReadLine(), RegexOptions.IgnoreCase);
            return filter != null;
        }

        public bool StaticIsMatch(string text)
        {
            return Regex.IsMatch(text, Environment.GetEnvironmentVariable("BIFROST_FILTER"));
        }

        public bool StaticIsMatchThroughLocal(string text)
        {
            var pattern = Console.ReadLine();
            return Regex.IsMatch(text, pattern, RegexOptions.CultureInvariant);
        }

        public Match StaticMatch(string text)
        {
            return Regex.Match(text, Console.ReadLine());
        }

        public MatchCollection StaticMatches(string text)
        {
            return Regex.Matches(text, Console.ReadLine(), RegexOptions.Multiline);
        }

        public string[] StaticSplit(string text)
        {
            return Regex.Split(text, Environment.GetEnvironmentVariable("BIFROST_SEPARATOR"));
        }

        public string StaticReplace(string text)
        {
            return Regex.Replace(text, Console.ReadLine(), "*");
        }

        public string StaticReplaceOptions(string text)
        {
            return Regex.Replace(text, Console.ReadLine(), "*", RegexOptions.IgnoreCase);
        }

        // Near misses: no finding expected below this line.
        public bool Escaped(string text)
        {
            return Regex.IsMatch(text, Regex.Escape(Console.ReadLine()));
        }

        public bool UntrustedInputConstantPattern()
        {
            return Regex.IsMatch(Console.ReadLine(), "^[a-z]+$");
        }

        public string UntrustedReplacementConstantPattern(string text)
        {
            return Regex.Replace(text, "[0-9]+", Console.ReadLine());
        }

        public bool StaticWithTimeout(string text)
        {
            return Regex.IsMatch(text, Console.ReadLine(), RegexOptions.None, TimeSpan.FromSeconds(1));
        }

        public string ReplaceWithTimeout(string text)
        {
            return Regex.Replace(text, Console.ReadLine(), "*", RegexOptions.None, TimeSpan.FromSeconds(1));
        }

        public bool ConstructorWithTimeout()
        {
            var filter = new Regex(Environment.GetEnvironmentVariable("BIFROST_FILTER"), RegexOptions.None, TimeSpan.FromSeconds(1));
            return filter != null;
        }

        public bool LocalLookalike(string text)
        {
            return Local.Regex.IsMatch(text, Console.ReadLine());
        }
    }
}

namespace Local
{
    public static class Regex
    {
        public static bool IsMatch(string input, string pattern) { return input == pattern; }
    }
}
