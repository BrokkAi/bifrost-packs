require "net/http"
require "cgi"

def handle(uri)
  Net::HTTP.get(uri)
  CGI.escapeElement("<b>x</b>", "script")
end
