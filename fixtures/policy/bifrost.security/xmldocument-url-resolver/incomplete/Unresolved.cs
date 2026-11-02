using System.Xml;

namespace Verify.XmlDocumentResolver.Incomplete
{
    public sealed class ConfigDocument : XmlDocument
    {
    }

    public sealed class UnresolvedWrites
    {
        private readonly XmlDocument _shared = new XmlDocument();

        // The engine does not infer the type of a `var` local.
        public void ImplicitlyTypedLocal(string postedXml)
        {
            var doc = new XmlDocument();
            doc.XmlResolver = new XmlUrlResolver();
            doc.LoadXml(postedXml);
        }

        // Object initializer members do not bind on Bifrost 0.14.2.
        public XmlDocument Initializer(string postedXml)
        {
            XmlDocument doc = new XmlDocument { XmlResolver = new XmlUrlResolver() };
            doc.LoadXml(postedXml);
            return doc;
        }

        // A field receiver does not bind on Bifrost 0.14.2.
        public void FieldReceiver(string postedXml)
        {
            _shared.XmlResolver = new XmlUrlResolver();
            _shared.LoadXml(postedXml);
        }

        // An inherited model member on a source subclass does not bind.
        public void Subclass(ConfigDocument config, string postedXml)
        {
            config.XmlResolver = new XmlUrlResolver();
            config.LoadXml(postedXml);
        }
    }
}
