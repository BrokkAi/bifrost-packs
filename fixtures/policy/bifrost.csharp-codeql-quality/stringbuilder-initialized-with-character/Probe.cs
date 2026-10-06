using System.Text;

class StringBuilderCases
{
    void Bad(char value)
    {
        var fromParameter = new StringBuilder(value);
        var fromLiteral = new StringBuilder('x');
    }

    void NearMiss()
    {
        var stringValue = new StringBuilder("x");
        var capacity = new StringBuilder(16);
    }
}
