package app

import java.io.File
import java.nio.file.Files
import java.nio.file.attribute.PosixFilePermissions

fun leakDir(secret: String) {
    val dir = createTempDir()
    File(dir, "token").writeText(secret)
}

fun leakFile(secret: String) {
    val f = createTempFile("export", ".json")
    f.writeText(secret)
}

fun qualified(secret: String) {
    val d = kotlin.io.createTempDir("x")
    File(d, "t").writeText(secret)
}

fun safe(secret: String) {
    val perms = PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------"))
    val dir = Files.createTempDirectory("app", perms)
    dir.resolve("token").toFile().writeText(secret)
}
