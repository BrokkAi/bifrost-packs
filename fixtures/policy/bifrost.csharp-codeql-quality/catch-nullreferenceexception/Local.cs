using System;

namespace Local
{
    public sealed class NullReferenceException : System.Exception { }

    public class LocalCatch
    {
        public int NearMissSourceType(Func<int> work)
        {
            try { return work(); }
            catch (NullReferenceException) { return 0; }
        }
    }
}
