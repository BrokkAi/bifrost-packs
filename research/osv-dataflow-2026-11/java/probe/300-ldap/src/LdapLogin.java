package ldap;

import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import javax.naming.directory.SearchControls;
import javax.naming.directory.SearchResult;
import javax.servlet.http.HttpServletRequest;
/** Inert LDAP filter cases for BrokkAi/bifrost-packs#300. */
public class LdapLogin {
    /** Positive: request input concatenated into the raw filter. */
    public boolean rawLogin(HttpServletRequest req, DirContext ctx) throws NamingException {
        String user = req.getParameter("user");
        NamingEnumeration<SearchResult> hits =
            ctx.search("ou=people,dc=example", "(uid=" + user + ")", new SearchControls());
        return hits.hasMore();
    }

    /** Positive: concrete InitialDirContext receiver. */
    public boolean concreteLogin(HttpServletRequest req, InitialDirContext ctx) throws NamingException {
        String user = req.getParameter("user");
        String filter = "(&(objectClass=person)(uid=" + user + "))";
        NamingEnumeration<SearchResult> hits = ctx.search("ou=people,dc=example", filter, new SearchControls());
        return hits.hasMore();
    }

    /** Near miss: input passed as a filter argument; the JDK escapes it. */
    public boolean parameterizedLogin(HttpServletRequest req, DirContext ctx) throws NamingException {
        String user = req.getParameter("user");
        NamingEnumeration<SearchResult> hits =
            ctx.search("ou=people,dc=example", "(uid={0})", new Object[] {user}, new SearchControls());
        return hits.hasMore();
    }

    /** Near miss: constant filter; input only reaches the base name. */
    public boolean constantFilter(HttpServletRequest req, DirContext ctx) throws NamingException {
        NamingEnumeration<SearchResult> hits =
            ctx.search("ou=people,dc=example", "(objectClass=person)", new SearchControls());
        return hits.hasMore();
    }
}
