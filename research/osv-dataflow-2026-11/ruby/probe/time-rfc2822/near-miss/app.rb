require "net/http"
require "time"

def handle(uri)
  Net::HTTP.get(uri)
  Time.rfc2822("Thu, 01 Jan 1970 00:00:00 +0000")
end
