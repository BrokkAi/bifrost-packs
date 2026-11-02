// Source: github/codeql/csharp/ql/test/query-tests/Bad Practices/EmptyCatchBlock/EmptyCatchBlock.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;

class EmptyCatchBlock
{
    void bad()
    {
        try
        {
        }
        catch (Exception)
        {
        } // $ Alert
    }

    void good()
    {
        try
        {
        }
        catch (Exception)
        {
            // GOOD: This catch block should be empty
        }
    }
}
