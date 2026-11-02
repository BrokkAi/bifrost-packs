using System.Security.Cryptography.Xml;
using System.Xml;

namespace Verify.SignedXmlKeyInfo.Incomplete
{
    public sealed class UnresolvedReceivers
    {
        private readonly SignedXml _signedXml;

        public UnresolvedReceivers(SignedXml signedXml)
        {
            _signedXml = signedXml;
        }

        // The engine does not infer the type of a `var` local.
        public bool ImplicitlyTypedLocal(XmlDocument assertion)
        {
            var signedXml = new SignedXml(assertion);
            return signedXml.CheckSignature();
        }

        // A field receiver does not bind on Bifrost 0.14.2.
        public bool FieldReceiver() => _signedXml.CheckSignature();
    }
}
