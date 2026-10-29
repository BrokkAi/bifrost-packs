using System;

public class NullCatchProbe
{
    public int Bad(string value)
    {
        try { return value.Length; }
        catch (NullReferenceException) { return 0; }
    }

    public int BadFiltered(string value, bool quiet)
    {
        try { return value.Length; }
        catch (System.NullReferenceException error) when (quiet) { return error.HResult; }
    }

    public int NearMissOther(string value)
    {
        try { return value.Length; }
        catch (InvalidOperationException) { return 0; }
    }
}
