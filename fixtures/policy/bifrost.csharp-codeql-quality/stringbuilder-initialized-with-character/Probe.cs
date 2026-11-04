using System.Text;

class StringBuilderCases
{
    void Bad(char glyph)
    {
        var fromParameter = new StringBuilder(glyph);
        var fromLiteral = new StringBuilder('x');
    }

    void NearMissLiterals()
    {
        var stringValue = new StringBuilder("x");
        var capacity = new StringBuilder(16);
    }

    void NearMissIntFormal(int value)
    {
        var capacity = new StringBuilder(value);
    }

    void NearMissStringFormal(string value)
    {
        var text = new StringBuilder(value);
    }
}
