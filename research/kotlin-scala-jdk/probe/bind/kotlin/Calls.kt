package bind

import java.io.FileOutputStream
import java.io.InputStream
import java.net.URL
import java.nio.file.Path
import java.util.zip.ZipEntry
import java.util.zip.ZipInputStream
import javax.crypto.Cipher
import javax.crypto.CipherInputStream
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.naming.directory.DirContext
import javax.naming.directory.SearchControls

fun zip(input: InputStream, root: Path) {
    val zis = ZipInputStream(input)
    val entry: ZipEntry = zis.getNextEntry()
    val name = entry.getName()
    val viaProperty = zis.nextEntry.name
    val target = root.resolve(name)
    FileOutputStream(target.toFile())
}

fun aead(input: InputStream, key: SecretKey, iv: ByteArray): InputStream {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
    return CipherInputStream(input, cipher)
}

fun ldap(ctx: DirContext, user: String) {
    ctx.search("ou=people", "(uid=" + user + ")", SearchControls())
}

fun url(address: String) {
    val url = URL(address)
    url.openConnection()
    System.getenv("HOME")
}
