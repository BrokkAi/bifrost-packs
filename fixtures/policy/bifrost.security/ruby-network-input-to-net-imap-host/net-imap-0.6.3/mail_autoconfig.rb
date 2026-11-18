require "net/http"
require "net/imap"

# Connects to the IMAP server that a mail autoconfiguration service names.
def connect_from_autoconfig(config_uri)
  host = Net::HTTP.get(config_uri)
  Net::IMAP.new(host, port: 993, ssl: true)
end

def connect_plain(config_uri)
  Net::IMAP.new(Net::HTTP.get(config_uri))
end

def connect_with_port(config_uri)
  host = Net::HTTP.get(config_uri)
  Net::IMAP.new(host, 143)
end

def connect_with_timeout(config_uri)
  host = Net::HTTP.get(config_uri)
  Net::IMAP.new(host, port: 993, ssl: true, open_timeout: 5)
end

def connect_to_configured_server(config_uri)
  Net::HTTP.get(config_uri)
  Net::IMAP.new("imap.example.com", port: 993, ssl: true)
end

def connect_on_published_port(config_uri)
  port = Net::HTTP.get(config_uri)
  Net::IMAP.new("imap.example.com", port: port)
end
