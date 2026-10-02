// Independently authored diagnostic fixture. No network request is made by this file.
import java.util.Hashtable;
import javax.naming.Context;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.directory.Attributes;
import javax.naming.directory.BasicAttribute;
import javax.naming.directory.BasicAttributes;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import javax.naming.directory.SearchControls;
import javax.naming.directory.SearchResult;

final class JndiFilterCases {
    static DirContext jdkLdap() throws NamingException {
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, "ldap://127.0.0.1:389");
        return new InitialDirContext(env);
    }

    static boolean rawLogin(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        String filter = "(uid=" + requestUid + ")";
        NamingEnumeration<SearchResult> hits = directory.search("ou=people", filter, new SearchControls());
        return hits.hasMore();
    }

    static boolean directInitialDirContext(String requestUid) throws NamingException {
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, "ldap://127.0.0.1:389");
        InitialDirContext directory = new InitialDirContext(env);
        return directory.search("ou=people", "(uid=" + requestUid + ")", new SearchControls()).hasMore();
    }

    static boolean aliasLogin(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        String alias = requestUid;
        return rawSearch(directory, "(uid=" + alias + ")").hasMore();
    }

    static NamingEnumeration<SearchResult> rawSearch(DirContext directory, String filter) throws NamingException {
        return directory.search("ou=people", filter, new SearchControls());
    }

    static boolean parameterizedLogin(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        return directory.search("ou=people", "(uid={0})", new Object[]{requestUid}, new SearchControls()).hasMore();
    }

    static boolean structuredLogin(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        Attributes attributes = new BasicAttributes(true);
        attributes.put(new BasicAttribute("uid", requestUid));
        return directory.search("ou=people", attributes).hasMore();
    }

    static boolean nonReaching(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        String fixed = "(uid=admin)";
        System.out.println(requestUid);
        return directory.search("ou=people", fixed, new SearchControls()).hasMore();
    }

    static void unrelatedResult(String requestUid) throws NamingException {
        DirContext directory = jdkLdap();
        directory.search("ou=people", "(uid=" + requestUid + ")", new SearchControls());
    }

    static boolean lookalike(String requestUid) {
        return new LocalDirectory().search("ou=people", "(uid=" + requestUid + ")", new SearchControls());
    }

    static final class LocalDirectory {
        boolean search(String name, String filter, SearchControls controls) { return false; }
    }
}
