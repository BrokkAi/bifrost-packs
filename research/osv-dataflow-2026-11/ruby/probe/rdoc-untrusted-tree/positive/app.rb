require "net/http"
require "rdoc"

def handle(uri)
  body = Net::HTTP.get(uri)
  RDoc::RDoc.new.document(body)
end
