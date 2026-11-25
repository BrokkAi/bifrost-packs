package app;

import java.sql.Statement;
import javax.servlet.http.HttpServletRequest;

/** Inert positive for the shipped servlet-to-JDBC rule. */
public class Dao {
    /** Positive: a request parameter concatenated into SQL text. */
    public void find(HttpServletRequest req, Statement st) throws Exception {
        String id = req.getParameter("id");
        st.executeQuery("SELECT * FROM t WHERE id = " + id);
    }
}
