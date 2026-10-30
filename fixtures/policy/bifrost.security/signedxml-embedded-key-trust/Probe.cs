using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Cryptography.Xml;
using System.Xml;

namespace Verify.SignedXmlKeyInfo
{
    public sealed class AssertionValidator
    {
        // Positive: the key comes from the posted assertion's own KeyInfo.
        public bool ValidateWithEmbeddedKey(XmlDocument assertion)
        {
            SignedXml signedXml = new SignedXml(assertion);
            XmlNodeList signatures = assertion.GetElementsByTagName("Signature", SignedXml.XmlDsigNamespaceUrl);
            signedXml.LoadXml((XmlElement)signatures[0]);
            return signedXml.CheckSignature();
        }

        // Positive: the caller hands over a SignedXml whose key it never pinned.
        public bool ValidateLoaded(SignedXml signedXml) => signedXml.CheckSignature();

        // Positive: the returned key is the document's key, not a trusted one.
        public bool ValidateReturningKey(SignedXml signedXml, out AsymmetricAlgorithm signingKey)
        {
            return signedXml.CheckSignatureReturningKey(out signingKey);
        }

        // Near miss: the certificate is pinned out of band.
        public bool ValidateWithPinnedCertificate(SignedXml signedXml, X509Certificate2 identityProvider)
        {
            return signedXml.CheckSignature(identityProvider, true);
        }

        // Near miss: the verification key is pinned out of band.
        public bool ValidateWithPinnedKey(SignedXml signedXml, RSA identityProviderKey)
        {
            return signedXml.CheckSignature(identityProviderKey);
        }

        // Near miss: an HMAC signature checked with a shared secret.
        public bool ValidateWithSharedSecret(SignedXml signedXml, HMACSHA256 sharedSecret)
        {
            return signedXml.CheckSignature(sharedSecret);
        }

        // Near miss: a same-named type that is not the framework SignedXml.
        public bool ValidateLocal(Local.Signatures.SignedXml local) => local.CheckSignature();
    }
}
