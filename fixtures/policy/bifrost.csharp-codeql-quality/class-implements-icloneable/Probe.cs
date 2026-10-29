using System;
using System.Collections.Generic;

namespace Probe
{
    interface IDocumentCloneable : ICloneable { }
    interface IVersionedDocument : IDocumentCloneable { }

    class Document : ICloneable
    {
        public object Clone() => new Document();
    }

    class Settings : System.ICloneable
    {
        object ICloneable.Clone() => new Settings();
    }

    class Draft : IDocumentCloneable
    {
        public object Clone() => new Draft();
    }

    class Revision : IVersionedDocument
    {
        public object Clone() => new Revision();
    }

    [Serializable]
    public abstract class Table<T> : List<Dictionary<int, string>>, global::System.ICloneable where T : struct
    {
        public object Clone() => null;
    }

    record Snapshot : ICloneable
    {
        public object Clone() => this;
    }

    class Point(int x) : ICloneable
    {
        public object Clone() => new Point(x);
    }

    interface IShape : ICloneable
    {
        new IShape Clone();
    }

    class Container
    {
        class Entry : ICloneable
        {
            public object Clone() => new Entry();
        }

        public object Clone() => new Container();
    }

    // Near misses.
    sealed class FrozenDocument : ICloneable
    {
        public object Clone() => new FrozenDocument();
    }

    struct Pixel : ICloneable
    {
        public object Clone() => this;
    }

    record struct Range : ICloneable
    {
        public object Clone() => this;
    }

    class DerivedDocument : Document
    {
        public new object Clone() => new DerivedDocument();
    }

    class Holder<T> where T : ICloneable
    {
        public object Clone() => null;
    }

    class CopierBase
    {
        public object Clone() => MemberwiseClone();
    }

    class Copier : CopierBase, ICloneable
    {
    }

    interface IPlainCloneable : ICloneable { }
}
