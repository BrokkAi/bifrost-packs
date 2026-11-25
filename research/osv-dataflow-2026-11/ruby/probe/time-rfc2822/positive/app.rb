require "net/http"
require "time"

def handle(uri)
  body = Net::HTTP.get(uri)
  Time.rfc2822(body)
end
