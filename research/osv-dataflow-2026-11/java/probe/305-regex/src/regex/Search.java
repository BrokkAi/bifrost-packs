package regex;

import java.util.regex.Pattern;
import javax.servlet.http.HttpServletRequest;
/** Inert regex cases for BrokkAi/bifrost-packs#305. */
public class Search {
    /** Positive: request input compiled as the pattern. */
    public boolean userPattern(HttpServletRequest req, String text) {
        String re = req.getParameter("re");
        return Pattern.matches(re, text);
    }

    /** Positive: compiled first. */
    public Pattern compileUserPattern(HttpServletRequest req) {
        return Pattern.compile(req.getParameter("re"));
    }

    /** Near miss: request input is only the subject text. */
    public boolean userText(HttpServletRequest req) {
        String text = req.getParameter("q");
        return Pattern.matches("[a-z]+", text);
    }

    /** Near miss: request input quoted before compiling. */
    public Pattern quoted(HttpServletRequest req) {
        return Pattern.compile(Pattern.quote(req.getParameter("re")));
    }
}
