package env

fun run() {
    val cmd = System.getenv("CMD")
    Runtime.getRuntime().exec(cmd)
}
