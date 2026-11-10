require "uri"
require "rexml/document"
require "net/imap"
require "json"

def stdlib_calls(text, host)
  URI.parse(text)
  REXML::Document.new(text)
  imap = Net::IMAP.new(host)
  imap.search(text)
  imap.uid_search(text)
  imap.fetch(1, text)
  imap.sort(["DATE"], text, "UTF-8")
  parser = JSON::ResumableParser.new
  parser.parse(text)
  parser.partial_value
end
