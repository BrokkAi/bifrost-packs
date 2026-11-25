require "net/http"
require "time"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  Time.rfc2822(body)
end
