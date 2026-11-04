namespace CsharpG08;

public class RecursiveEqualsProbe
{
    public override bool Equals(object other)
    {
        object different = other;
        return Equals(other) && Equals(different);
    }

    public bool Equals(RecursiveEqualsProbe other)
    {
        return other != null;
    }

    public bool Compare(RecursiveEqualsProbe other)
    {
        return Equals(other);
    }

    public bool ExplicitReceiver(object other, object obj)
    {
        return other.Equals(obj);
    }

    public bool CastedEquals(object other)
    {
        return Equals((RecursiveEqualsProbe)other);
    }
}
