require "net/http"
require "time"
require "cgi"
require "rexml/document"
require "net/imap"
require "rdoc"
require "rubygems/installer"

def stdlib_calls(uri, text)
  body = Net::HTTP.get(uri)
  Time.rfc2822(text)
  CGI::Cookie.parse(text)
  CGI.escapeElement(text, "script")
  REXML::Document.new(text)
  Net::IMAP.new(text)
  Net::IMAP.new(text, port: 993)
  RDoc::RDoc.new.document(text)
  Gem::Installer.at(text)
  body
end
