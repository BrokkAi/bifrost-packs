using System;
using System.IO;

public class EmptyCatchProbe
{
    public void BadTyped(Action work)
    {
        try { work(); }
        catch (InvalidOperationException) { }
    }

    public void BadUntyped(Action work)
    {
        try { work(); }
        catch { }
    }

    public void BadFiltered(Action work, bool quiet)
    {
        try { work(); }
        catch (Exception) when (quiet) { }
    }

    public void BadUnmodeledType(Action work)
    {
        try { work(); }
        catch (IOException) { }
    }

    public void NearMissLineComment(Action work)
    {
        try { work(); }
        catch (InvalidOperationException)
        {
            // Expected when the queue is already drained.
        }
    }

    public void NearMissBlockComment(Action work)
    {
        try { work(); }
        catch { /* best effort */ }
    }

    public void NearMissStatement(Action work)
    {
        try { work(); }
        catch (Exception error) { Console.Error.WriteLine(error); }
    }

    public void NearMissRethrow(Action work)
    {
        try { work(); }
        catch (Exception) { throw; }
    }

    public void NearMissEmptyStatement(Action work)
    {
        try { work(); }
        catch (Exception) { ; }
    }

    public void NearMissNestedBlock(Action work)
    {
        try { work(); }
        catch (Exception) { { } }
    }

    public void NearMissEmptyFinally(Action work)
    {
        try { work(); }
        finally { }
    }
}
