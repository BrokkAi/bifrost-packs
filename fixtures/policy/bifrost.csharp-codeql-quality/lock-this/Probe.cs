using System;

public class LockThisProbe
{
    private readonly object _sync = new object();
    private readonly object sync = new object();
    private int count;

    public void BadThis()
    {
        lock (this)
        {
            count++;
        }
    }

    public void BadParenthesized()
    {
        lock ((this)) { count++; }
    }

    public void BadInLambda(Action<Action> run)
    {
        run(() => { lock (this) { count--; } });
    }

    public int BadInProperty
    {
        get { lock (this) { return count; } }
    }

    public void NearMissPrivateField()
    {
        lock (_sync) { count++; }
    }

    public void NearMissFieldThroughThis()
    {
        lock (this.sync) { count++; }
    }

    public void NearMissCast()
    {
        lock ((object)this) { count++; }
    }

    public void NearMissTypeof()
    {
        lock (typeof(LockThisProbe)) { count++; }
    }

    public void NearMissThisInBody()
    {
        lock (_sync) { Console.WriteLine(this); }
    }
}

public class LockThisBaseProbe : LockThisProbe
{
    public void NearMissBase()
    {
        lock (base.ToString()) { }
    }
}
