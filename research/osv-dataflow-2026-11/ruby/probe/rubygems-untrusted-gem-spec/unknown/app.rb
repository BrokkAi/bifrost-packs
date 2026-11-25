require "net/http"
require "rubygems/installer"

def handle(uri)
  body = Opaque.transform(Net::HTTP.get(uri))
  Gem::Installer.at(body)
end
