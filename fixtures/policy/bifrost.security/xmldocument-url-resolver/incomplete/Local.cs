namespace Local.Xml
{
    public class XmlUrlResolver
    {
        public XmlUrlResolver()
        {
        }
    }

    // A same-named source type. Its member is not System.Xml.XmlDocument.XmlResolver,
    // but Bifrost 0.14.2 rejects the source member binding, so the run stays
    // inconclusive instead of treating it as a near miss.
    public sealed class XmlDocument
    {
        public XmlUrlResolver XmlResolver;
    }

    public static class Configure
    {
        public static void Apply(XmlDocument document) => document.XmlResolver = new XmlUrlResolver();
    }
}
