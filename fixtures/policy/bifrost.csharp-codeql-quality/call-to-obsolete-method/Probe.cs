using System;
using AliasObsolete = System.ObsoleteAttribute;

class Service
{
    [Obsolete]
    public void Old() { }

    [ObsoleteAttribute]
    public void OldWithSuffix() { }

    [System.Obsolete]
    public void QualifiedOld() { }

    public void Caller()
    {
        Old();
        OldWithSuffix();
        QualifiedOld();
    }

    public void ExplicitCaller(Service service)
    {
        service.Old();
        service.OldWithSuffix();
        service.QualifiedOld();
    }

    [AliasObsolete]
    public void LegacyCaller()
    {
        Old();
    }
}

[Obsolete]
class LegacyCallerType
{
    [Obsolete]
    public void Old() { }

    public void Call(Service service)
    {
        service.Old();
    }
}

class Unrelated
{
    public void Old() { }

    public void Caller()
    {
        Old();
    }
}
