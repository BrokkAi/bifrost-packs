require "net/http"
require "rexml/document"

def handle(uri)
  Net::HTTP.get(uri)
  REXML::Document.new("<feed/>")
end
