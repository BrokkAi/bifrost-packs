// Source: github/codeql/csharp/ql/src/Bad Practices/UseOfSystemOutputStream.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;
using System.IO;

namespace UseOfSystemOutputStream.cs
{
    class Main
    {

        public void Foo(string s, TextWriter t)
        {

            Console.WriteLine("string: " + s);  // BAD

            t.WriteLine(s); // GOOD

            t = Console.Out; // BAD

            t.WriteLine(s); // GOOD

            Console.SetError(t); // GOOD

            t = Console.Error; // GOOD

        }

    }

}
