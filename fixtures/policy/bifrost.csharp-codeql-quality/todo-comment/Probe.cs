public class TodoProbe
{
    // TODO: replace the fixed retry count
    private int retries = 3;

    /* FIXME: this block comment spans
       more than one line */
    public int Retries() => retries;

    /// <summary>XXX: documentation comments are comments too.</summary>
    public void Documented() { }

    // Near miss: lowercase markers such as todo and fixme are ignored.
    // Near miss: an assignment-like marker such as mode=XXX is ignored.
    public string Marker() => "TODO is a string literal, not a comment";
}
