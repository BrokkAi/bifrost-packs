require "net/http"
require "rexml/document"

DEFAULT_FEED = "<feed><entry title='welcome'/></feed>"

def import_feed(feed_uri)
  body = Net::HTTP.get(feed_uri)
  REXML::Document.new(body)
end

def import_inline(feed_uri)
  REXML::Document.new(Net::HTTP.get(feed_uri))
end

def default_feed
  REXML::Document.new(DEFAULT_FEED)
end
