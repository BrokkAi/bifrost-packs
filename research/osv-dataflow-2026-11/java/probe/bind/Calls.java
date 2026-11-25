import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.Pattern;
import java.util.zip.*;
import javax.naming.*;
import javax.naming.directory.*;
import javax.xml.parsers.*;
import java.beans.XMLDecoder;
import com.sun.net.httpserver.HttpExchange;

class Calls {
    Object sockets(ServerSocket server) throws Exception {
        Socket s = server.accept();
        InputStream in = s.getInputStream();
        ObjectInputStream ois = new ObjectInputStream(in);
        ois.setObjectInputFilter(ObjectInputFilter.Config.createFilter("java.base/*;!*"));
        return ois.readObject();
    }
    Object urls(String address) throws Exception {
        URL url = new URL(address);
        URLConnection c = url.openConnection();
        return new ObjectInputStream(c.getInputStream()).readObject();
    }
    void zips(InputStream in, File dir, Path root) throws Exception {
        ZipInputStream zis = new ZipInputStream(in);
        ZipEntry e = zis.getNextEntry();
        String name = e.getName();
        File f = new File(dir, name);
        String canon = f.getCanonicalPath();
        boolean ok = canon.startsWith(dir.getCanonicalPath());
        Path p = root.resolve(name).normalize();
        boolean ok2 = p.startsWith(root);
        FileOutputStream out = new FileOutputStream(f);
        Files.copy(zis, p);
        out.close();
    }
    Object jndi(String name, String user) throws Exception {
        Context ctx = new InitialContext();
        Object o = ctx.lookup(name);
        DirContext dctx = new InitialDirContext(new Hashtable<String, String>());
        dctx.search("ou=people", "(uid=" + user + ")", new SearchControls());
        dctx.search("ou=people", "(uid={0})", new Object[] {user}, new SearchControls());
        return o;
    }
    boolean regex(String re, String text) {
        Pattern p = Pattern.compile(re);
        boolean a = p.matcher(text).matches();
        return a || text.matches(re) || Pattern.matches(re, text);
    }
    void process(List<String> args) throws Exception {
        ProcessBuilder pb = new ProcessBuilder(args);
        pb.start();
    }
    void xml(InputStream in) throws Exception {
        DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
        f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
        DocumentBuilder b = f.newDocumentBuilder();
        b.parse(in);
        new XMLDecoder(in).readObject();
    }
    String env() {
        return System.getProperty("x") + System.getenv("Y");
    }
    void http(HttpExchange ex) throws Exception {
        URI u = ex.getRequestURI();
        String q = u.getQuery();
        InputStream body = ex.getRequestBody();
        new ObjectInputStream(body).readObject();
    }
}
