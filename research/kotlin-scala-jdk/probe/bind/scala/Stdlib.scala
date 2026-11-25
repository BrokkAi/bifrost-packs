package bind

import scala.sys.process.Process
import scala.util.matching.Regex

object Stdlib {
  def stdlib(command: String, text: String): Boolean = {
    val exit = Process(command).!
    val pattern: Regex = "^(a+)+$".r
    pattern.matches(text) && exit == 0
  }
}
