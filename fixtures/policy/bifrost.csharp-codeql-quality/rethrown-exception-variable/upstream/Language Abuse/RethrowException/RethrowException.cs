// Source: github/codeql/csharp/ql/test/query-tests/Language Abuse/RethrowException/RethrowException.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;

class C
{
    static void Main(string[] args)
    {
        try
        {
        }
        catch (Exception e)
        {
            throw e;    // $ Alert // BAD
        }

        try
        {
        }
        catch (Exception e)
        {
            if (true)
                throw e;    // $ Alert // BAD
        }

        try
        {
        }
        catch (Exception e)
        {
            throw;    // GOOD
        }

        try
        {
        }
        catch (Exception e)
        {
            try
            {
            }
            catch
            {
                throw e;  // GOOD
            }
        }
    }
}
