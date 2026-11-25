require "net/http"
require "cgi"

def handle(uri)
  body = Net::HTTP.get(uri)
  CGI::Cookie.parse(body)
end
