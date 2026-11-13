require "net/http"
require "rubygems/installer"

module MirrorAgent
  def self.install_next(control_uri)
    gem_path = ArchiveCache.store(Net::HTTP.get(control_uri))
    Gem::Installer.at(gem_path).install
  end
end
