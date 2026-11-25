require "net/http"
require "rubygems/installer"

def handle(uri)
  Net::HTTP.get(uri)
  Gem::Installer.at("pkg/own.gem")
end
