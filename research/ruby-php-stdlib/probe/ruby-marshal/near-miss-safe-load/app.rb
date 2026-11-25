require "net/http"

def fetch_blob(uri)
  body = Net::HTTP.get(uri)
  Psych.safe_load(body)
end
