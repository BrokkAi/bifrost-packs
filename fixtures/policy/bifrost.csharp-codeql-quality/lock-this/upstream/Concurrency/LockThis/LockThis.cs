// Source: github/codeql/csharp/ql/test/query-tests/Concurrency/LockThis/LockThis.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;

class Program
{
    Object lck = new Object();

    void f()
    {
        lock (this)  // $ Alert // Not OK
        {
        }

        lock (lck)   // OK
        {
        }
    }
}
