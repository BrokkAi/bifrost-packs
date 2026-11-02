// Source: github/codeql/csharp/ql/test/query-tests/Likely Bugs/BadCheckOdd/BadCheckOdd.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;

namespace ConsoleApplication2
{
    class Program
    {

        static void Main(string[] args)
        {
            int a = 2;

            // BAD
            if (a % 2 == 1) // $ Alert
                Console.Out.WriteLine("a is odd");
            if (a % 2 != 1) // $ Alert
                Console.Out.WriteLine("a is even");
            if (a % 2 > 0) // $ Alert
                Console.Out.WriteLine("a is odd");
            if ((a % 2) > 0) // $ Alert
                Console.Out.WriteLine("a is odd");

            // GOOD
            if (a % 2 == 0)
                Console.Out.WriteLine("a is even");
            if (a % 2 != 0)
                Console.Out.WriteLine("a is odd");
            if (a % 2 > 1)
                Console.Out.WriteLine("a is very odd");
            if (args.Length % 2 == 1)
                Console.Out.WriteLine("args.Length is odd");
            if (args.Count() % 2 == 1)
                Console.Out.WriteLine("args.Count() is odd");
        }
    }
}
