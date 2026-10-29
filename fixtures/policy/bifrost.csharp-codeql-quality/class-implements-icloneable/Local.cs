namespace Local
{
    interface ICloneable
    {
        object Clone();
    }

    // Near miss: the base list names this source interface, not System.ICloneable.
    class Widget : ICloneable
    {
        public object Clone() => new Widget();
    }
}
