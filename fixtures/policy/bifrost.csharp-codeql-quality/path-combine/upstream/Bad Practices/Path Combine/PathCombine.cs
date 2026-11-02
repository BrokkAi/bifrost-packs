// Source: github/codeql/csharp/ql/test/query-tests/Bad Practices/Path Combine/PathCombine.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System.IO;

class PathCombine
{
    void bad()
    {
        Path.Combine(@"C:\Users", @"C:\Program Files"); // $ Alert
    }

    void good()
    {
        Path.Join(@"C:\Users", @"C:\Program Files");
    }
}
