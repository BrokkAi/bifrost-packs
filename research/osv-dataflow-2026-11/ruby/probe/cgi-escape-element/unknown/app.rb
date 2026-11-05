require "net/http"
require "cgi"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  CGI.escapeElement(body, "script")
end
