require "net/http"

def fetch_blob(uri)
  body = Net::HTTP.get(uri)
  Marshal.load(body)
end
