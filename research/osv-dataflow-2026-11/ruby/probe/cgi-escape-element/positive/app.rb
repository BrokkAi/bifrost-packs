require "net/http"
require "cgi"

def handle(uri)
  body = Net::HTTP.get(uri)
  CGI.escapeElement(body, "script")
end
