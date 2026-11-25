require "net/http"

class Codec
  def self.load(bytes) = bytes.bytesize
end

def fetch_blob(uri)
  body = Net::HTTP.get(uri)
  Codec.load(body)
end
