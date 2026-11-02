using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

static class Geometry
{
    public static void Normalize(ref double x, ref double y, ref double z) { }

    public static void Swap3<T>(ref T a, ref T b, ref T c) where T : struct { }

    public static void Shift(this ref int value, ref int min, scoped ref int max) { }

    public static void Merge(
        [In] ref int count,
        ref Dictionary<string, List<int>> index,
        ref readonlyCounter counter)
    {
    }

    // Near misses.
    public static void TwoRefsAndOut(ref int a, ref int b, out int c) { c = a + b; }

    public static void ReadonlyRefs(in int a, ref readonly int b, ref int c, ref int d) { }

    public static void WithDefaults(ref int a, ref int b, int c = 0, string note = "ref x, ref y") { }

    public static int Forward(ref int a, int b) => Use(ref a, ref b, ref a);

    public static void Body(ref int a)
    {
        Use(ref a, ref a, ref a);
    }

    static int Use(ref int a, ref int b, int c) => a + b + c;

    public static void Outer()
    {
        void Local(ref int a, ref int b, ref int c) { }
    }
}

struct readonlyCounter { }

interface IAccumulator
{
    void Accumulate(ref long sum, ref long count, ref long max);
}

class Accumulator
{
    public Accumulator(ref int a, ref int b, ref int c) { }

    public delegate void Callback(ref int a, ref int b, ref int c);

    public static Accumulator operator +(Accumulator x, Accumulator y) => x;
}
