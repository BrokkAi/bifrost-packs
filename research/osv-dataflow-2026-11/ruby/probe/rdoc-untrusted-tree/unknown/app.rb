require "net/http"
require "rdoc"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  RDoc::RDoc.new.document(body)
end
