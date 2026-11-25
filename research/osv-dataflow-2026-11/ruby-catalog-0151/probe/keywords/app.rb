require "net/imap"

def fetch_changed(imap_host, attr, since)
  imap = Net::IMAP.new(imap_host)
  imap.fetch(1, attr)
  imap.fetch(1, attr, changedsince: since)
end
