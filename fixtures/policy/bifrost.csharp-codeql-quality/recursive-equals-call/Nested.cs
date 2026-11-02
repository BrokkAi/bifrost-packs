using System;

namespace CsharpG08;

public class NestedEqualsProbe
{
    public override bool Equals(object other)
    {
        Func<bool> deferred = () => Equals(other);
        return deferred != null;
    }

    public bool UnresolvedElsewhere(dynamic value, object other)
    {
        return value.Equals(other) && Missing.Shared.Equals(other);
    }
}
