// Source: github/codeql/csharp/ql/test/query-tests/API Abuse/CallToGCCollect/CallToGCCollectBad.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;

class Bad
{
    void M()
    {
        GC.Collect(); // $ Alert
    }
}
