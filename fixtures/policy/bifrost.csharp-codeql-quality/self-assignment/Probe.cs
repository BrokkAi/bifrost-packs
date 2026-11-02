using System;
using System.Collections.Generic;

class Options
{
    public int Count { get; set; }
    public int Size;
}

record Shape(int Count);

class Probe
{
    int count;
    int size;
    int[] slots = new int[4];

    Probe(int count, int size)
    {
        count = count;
        this.size = size;
    }

    void Locals(int a, int b, object o, string s, List<int> xs)
    {
        a = a;
        a = b;
        a += a;
        int local = b;
        local = local;
        if (o is int n) { n = n; }
        int.TryParse(s, out var parsed);
        parsed = parsed;
        foreach (var x in xs) { var y = x; y = y; }
        Func<int, int> f = c => { c = c; return c; };
        Action g = () => { local = local; };
        int copy = a;
        copy = local;
    }

    void Members(Probe other, int Count, Shape shape)
    {
        this.count = this.count;
        size = size;
        other.size = other.size;
        slots[0] = slots[0];
        this.count = count;
        var options = new Options { Count = Count };
        var anonymous = new { Count = Count };
        var reshaped = shape with { Count = Count };
    }
}
