// Source: github/codeql/csharp/ql/test/query-tests/Likely Bugs/RandomUsedOnce/RandomUsedOnce.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;

class RandomTest
{
    void f()
    {
        new Random().Next();  // $ Alert // BAD

        byte[] buffer = new byte[10];
        new Random().NextBytes(buffer); // $ Alert // BAD

        new Random().NextDouble();  // $ Alert // BAD
        new Random().Next(10);      // $ Alert // BAD
        new Random().Next(10, 20);   // $ Alert // BAD

        new Random().Equals(null);  // GOOD
    }
}
