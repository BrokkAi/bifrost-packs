namespace Local
{
    public sealed class Random
    {
        public Random() { }
        public int Next() { return 4; }
    }

    public class LocalRandomUse
    {
        public int NearMissSourceType()
        {
            return new Random().Next();
        }
    }
}
