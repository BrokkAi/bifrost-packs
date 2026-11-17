require "net/http"

module Deploy
  # An application class whose `at` only records the requested archive name.
  class Installer
    def self.at(path)
      new(path)
    end

    def initialize(path)
      @path = path
    end
  end

  def self.queue_install(control_uri)
    requested = Net::HTTP.get(control_uri)
    Installer.at(requested)
  end
end
