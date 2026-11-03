package bind;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Path;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import javax.crypto.Cipher;
import javax.crypto.CipherInputStream;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.naming.directory.DirContext;
import javax.naming.directory.SearchControls;

public class Calls {
    static void zip(InputStream input, Path root) throws Exception {
        ZipInputStream zis = new ZipInputStream(input);
        ZipEntry entry = zis.getNextEntry();
        String name = entry.getName();
        Path target = root.resolve(name);
        new FileOutputStream(target.toFile());
    }

    static InputStream aead(InputStream input, SecretKey key, byte[] iv) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv));
        return new CipherInputStream(input, cipher);
    }

    static void ldap(DirContext ctx, String user) throws Exception {
        ctx.search("ou=people", "(uid=" + user + ")", new SearchControls());
    }

    static void url(String address) throws Exception {
        URL url = new URL(address);
        url.openConnection();
        System.getenv("HOME");
    }
}
