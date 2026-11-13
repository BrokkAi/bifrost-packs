require "net/http"
require "rexml/document"

def import_feed(feed_uri)
  body = FeedCache.fetch(feed_uri) { Net::HTTP.get(feed_uri) }
  REXML::Document.new(body)
end
