require "net/http"
require "net/imap"

# Connects with options forwarded as a keyword splat.
def connect_with_options(config_uri, options)
  host = Net::HTTP.get(config_uri)
  Net::IMAP.new(host, **options)
end
