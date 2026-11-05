require "net/http"
require "cgi"

def handle(uri)
  Net::HTTP.get(uri)
  CGI::Cookie.parse("session=abc")
end
