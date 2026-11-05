require "net/http"
require "net/imap"

def handle(uri)
  Net::HTTP.get(uri)
  Net::IMAP.new("imap.example.com", port: 993, ssl: true)
end
