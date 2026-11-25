require "net/http"
require "rexml/document"

def handle(uri)
  body = Net::HTTP.get(uri)
  REXML::Document.new(body)
end
