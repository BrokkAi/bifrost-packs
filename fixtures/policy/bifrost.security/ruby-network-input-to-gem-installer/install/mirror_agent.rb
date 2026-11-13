require "net/http"
require "rubygems/installer"

module MirrorAgent
  # The control service names the cached archive this host should install.
  def self.install_next(control_uri)
    gem_path = Net::HTTP.get(control_uri)
    Gem::Installer.at(gem_path).install
  end

  def self.install_staged(control_uri)
    installer = Gem::Installer.at(Net::HTTP.get(control_uri))
    installer.install
  end

  def self.prepare_next(control_uri)
    Gem::Installer.at(Net::HTTP.get(control_uri))
  end

  def self.install_vendored
    Gem::Installer.at("vendor/cache/billing-client-2.4.0.gem").install
  end
end
