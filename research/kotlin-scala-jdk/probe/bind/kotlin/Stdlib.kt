package bind

import javax.crypto.spec.SecretKeySpec

fun stdlib(input: String): Int {
    val parsed = runCatching { input.toInt() }
    val key = SecretKeySpec("0123456789abcdef".toByteArray(), "AES")
    return parsed.getOrElse { key.encoded.size }
}
