using System;

public class EmptyLockProbe
{
    private readonly object _sync = new object();
    private int count;

    public void BadEmpty()
    {
        lock (_sync) { }
    }

    public void BadLineComment()
    {
        lock (_sync)
        {
            // count++;
        }
    }

    public void BadBlockComment()
    {
        lock (_sync) { /* wait for the writer */ }
    }

    public void BadRegion()
    {
        lock (_sync)
        {
            #region drained
            #endregion
        }
    }

    public void BadInLambda(Action<Action> run)
    {
        run(() => { lock (_sync) { } });
    }

    public void NearMissStatement()
    {
        lock (_sync) { count++; }
    }

    public void NearMissEmptyStatement()
    {
        lock (_sync) { ; }
    }

    public void NearMissNestedBlock()
    {
        lock (_sync) { { } }
    }

    public void NearMissNotBlock()
    {
        lock (_sync) ;
    }

    public void NearMissEmptyBlockAfterLock()
    {
        lock (_sync) { count++; }
        { }
    }

    public void NearMissOuterLock()
    {
        lock (_sync) lock (this) { count++; }
    }
}
