using System;

public class RethrowProbe
{
    public void BadFiltered(int code)
    {
        try { Work(); }
        catch (InvalidOperationException error) when (code > 0)
        {
            Log(error);
            throw error;
        }
    }

    public void BadAlongsideBareThrow(bool retry)
    {
        try { Work(); }
        catch (Exception error)
        {
            if (retry) { throw; }
            throw error;
        }
    }

    public void NearMissWrapped()
    {
        try { Work(); }
        catch (Exception error)
        {
            throw new InvalidOperationException("work failed", error);
        }
    }

    public void NearMissOtherVariable(Exception saved)
    {
        try { Work(); }
        catch (Exception error)
        {
            Log(error);
            throw saved;
        }
    }

    public Action NearMissLambda()
    {
        try { Work(); return () => { }; }
        catch (Exception error)
        {
            return () => throw error;
        }
    }

    public void NearMissLocalFunction()
    {
        try { Work(); }
        catch (Exception error)
        {
            void Raise() { throw error; }
            Log(error);
        }
    }

    private void Work() { }
    private void Log(Exception error) { }
}
