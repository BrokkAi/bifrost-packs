require "net/http"
require "net/imap"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  Net::IMAP.new(body, port: 993, ssl: true)
end
