using System;

public class CatchRules
{
    public void BadEmpty()
    {
        try { }
        catch { }
    }

    public int BadBare()
    {
        try { return 1; }
        catch { return 0; }
    }

    public int BadSystem()
    {
        try { return 1; }
        catch (Exception ex) { return ex.HResult; }
    }

    public int GoodSpecific()
    {
        try { return 1; }
        catch (InvalidOperationException) { return 0; }
    }

    public int GoodRethrow()
    {
        try { return 1; }
        catch (Exception) { throw; }
    }

    public int GoodFilter()
    {
        try { return 1; }
        catch (Exception ex) when (ex.HResult != 0) { return 0; }
    }

    public int GoodVariableRethrow()
    {
        try { return 1; }
        catch (Exception ex) { throw ex; }
    }

    public int GoodSourceSpecific()
    {
        try { return 1; }
        catch (LocalException) { return 0; }
    }
}

public sealed class LocalException : Exception { }
