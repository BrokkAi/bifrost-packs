package env

object Main {
  def run(): Unit = {
    val cmd = System.getenv("CMD")
    Runtime.getRuntime().exec(cmd)
  }
}
