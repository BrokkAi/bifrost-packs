require "net/http"
require "rexml/document"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  REXML::Document.new(body)
end
