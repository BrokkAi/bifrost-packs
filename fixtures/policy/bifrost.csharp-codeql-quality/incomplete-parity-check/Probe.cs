using System;
using System.Collections.Generic;
using System.Linq;

public class ParityProbe
{
    public void Bad(int x, long n, List<int> items)
    {
        bool odd = x % 2 == 1;
        bool even = x % 2 != 1;
        bool positive = (x % 2) > 0;
        bool wide = n % 2L == 1L;
        bool cast = (long)x % 2 == 1;
        bool count = items.Count % 2 == 1;
        while (x % 2 == 1) { x--; }
    }

    public void NearMiss(int x, string[] args, IEnumerable<int> values)
    {
        bool even = x % 2 == 0;
        bool odd = x % 2 != 0;
        bool abs = Math.Abs(x % 2) == 1;
        bool third = x % 3 == 1;
        bool negative = x % 2 == -1;
        bool atLeast = x % 2 >= 1;
        bool flipped = 1 == x % 2;
        bool real = x % 2 == 1.0;
        bool pattern = x % 2 is 1;
        bool length = args.Length % 2 == 1;
        bool castLength = (long)args.Length % 2 == 1;
        bool counted = values.Count() % 2 == 1;
        bool literal = 7 % 2 == 1;
    }
}
