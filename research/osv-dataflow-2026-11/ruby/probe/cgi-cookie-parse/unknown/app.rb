require "net/http"
require "cgi"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  CGI::Cookie.parse(body)
end
