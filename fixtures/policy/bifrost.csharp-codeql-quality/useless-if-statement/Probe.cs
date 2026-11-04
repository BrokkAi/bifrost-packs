namespace Fixture
{
    class Probe
    {
        void Bad(bool condition)
        {
            if (condition) ;
            if (condition) { }
        }

        void Good(bool condition)
        {
            if (condition) { } else { Work(); }
        }

        void NearMiss(bool condition)
        {
            if (condition) { Work(); }
        }

        void Work() { }
    }
}
