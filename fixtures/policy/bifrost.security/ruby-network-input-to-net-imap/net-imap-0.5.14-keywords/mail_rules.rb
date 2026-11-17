require "net/http"
require "net/imap"

def apply_rules(rules_uri, host)
  criteria = Net::HTTP.get(rules_uri)
  imap = Net::IMAP.new(host, port: 993, ssl: true)
  imap.search(criteria)
end
