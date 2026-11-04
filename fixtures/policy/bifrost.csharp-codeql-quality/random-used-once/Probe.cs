using System;

public class RandomProbe
{
    public int BadSeeded(int seed)
    {
        return new Random(seed).Next(1, 7);
    }

    public void BadSpan(Span<byte> buffer)
    {
        new Random().NextBytes(buffer);
    }

    public int KnownMissParenthesized()
    {
        return (new Random()).Next();
    }

    public int BadQualified()
    {
        return new System.Random().Next();
    }

    public int NearMissKept()
    {
        var random = new Random();
        return random.Next();
    }

    public long NearMissOtherMethod()
    {
        return new Random().NextInt64();
    }

    public int NearMissShared()
    {
        return Random.Shared.Next();
    }

    public int NearMissSubclass()
    {
        return new SeededRandom().Next();
    }
}

public class SeededRandom : Random
{
    public SeededRandom() : base(42) { }
}
