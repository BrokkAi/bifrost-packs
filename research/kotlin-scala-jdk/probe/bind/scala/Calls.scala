package bind

import java.io.{FileOutputStream, InputStream}
import java.net.URL
import java.nio.file.Path
import java.util.zip.{ZipEntry, ZipInputStream}
import javax.crypto.{Cipher, CipherInputStream, SecretKey}
import javax.crypto.spec.GCMParameterSpec
import javax.naming.directory.{DirContext, SearchControls}

object Calls {
  def zip(input: InputStream, root: Path): Unit = {
    val zis = new ZipInputStream(input)
    val entry: ZipEntry = zis.getNextEntry()
    val name = entry.getName
    val target = root.resolve(name)
    new FileOutputStream(target.toFile)
  }

  def aead(input: InputStream, key: SecretKey, iv: Array[Byte]): InputStream = {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv))
    new CipherInputStream(input, cipher)
  }

  def ldap(ctx: DirContext, user: String): Unit = {
    ctx.search("ou=people", "(uid=" + user + ")", new SearchControls())
  }

  def url(address: String): Unit = {
    val url = new URL(address)
    url.openConnection()
    System.getenv("HOME")
  }
}
