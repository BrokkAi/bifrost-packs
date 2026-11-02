using System.IO;
using System.Xml;

namespace Verify.XmlDocumentResolver
{
    public sealed class DocumentLoader
    {
        // Positive: the posted XML is parsed with external entity resolution.
        public XmlDocument LoadPosted(string postedXml)
        {
            XmlDocument doc = new XmlDocument();
            doc.XmlResolver = new XmlUrlResolver();
            doc.LoadXml(postedXml);
            return doc;
        }

        // Positive: the caller's document is configured before the request body is loaded.
        public void LoadBody(XmlDocument document, Stream body)
        {
            document.XmlResolver = new XmlUrlResolver();
            document.Load(body);
        }

        // Reported, a known limit: the file is trusted, but the policy does not
        // establish where the XML comes from.
        public XmlDocument LoadBundledConfig()
        {
            XmlDocument config = new XmlDocument();
            config.XmlResolver = new XmlUrlResolver();
            config.Load(Path.Combine("config", "app.xml"));
            return config;
        }

        // Near miss: the default XmlDocument resolver.
        public XmlDocument LoadDefault(string postedXml)
        {
            XmlDocument doc = new XmlDocument();
            doc.LoadXml(postedXml);
            return doc;
        }

        // Near miss: external resolution is switched off explicitly.
        public XmlDocument LoadWithoutResolver(string postedXml)
        {
            XmlDocument doc = new XmlDocument();
            doc.XmlResolver = null;
            doc.LoadXml(postedXml);
            return doc;
        }

        // Near miss: DTDs are prohibited, so the resolver is never asked for an entity.
        public XmlReader ProhibitedDtd(Stream body)
        {
            XmlReaderSettings settings = new XmlReaderSettings();
            settings.DtdProcessing = DtdProcessing.Prohibit;
            settings.XmlResolver = new XmlUrlResolver();
            return XmlReader.Create(body, settings);
        }

        // Near miss: DTDs are parsed but external resources cannot be resolved.
        public XmlReader ParsedDtdWithoutResolver(Stream body)
        {
            XmlReaderSettings settings = new XmlReaderSettings();
            settings.DtdProcessing = DtdProcessing.Parse;
            settings.XmlResolver = null;
            return XmlReader.Create(body, settings);
        }

        // Near miss: a legacy reader with resolution switched off.
        public XmlTextReader LegacyReaderWithoutResolver(Stream body)
        {
            XmlTextReader reader = new XmlTextReader(body);
            reader.XmlResolver = null;
            return reader;
        }
    }
}
