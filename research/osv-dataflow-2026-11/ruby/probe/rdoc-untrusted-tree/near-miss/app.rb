require "net/http"
require "rdoc"

def handle(uri)
  Net::HTTP.get(uri)
  RDoc::RDoc.new.document(["lib"])
end
