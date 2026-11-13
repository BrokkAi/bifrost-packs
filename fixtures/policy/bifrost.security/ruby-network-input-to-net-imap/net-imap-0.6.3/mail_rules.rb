require "net/http"
require "net/imap"

# Applies mailbox rules published by a remote rules service.
def apply_rules(rules_uri, host, user, password)
  criteria = Net::HTTP.get(rules_uri)
  imap = Net::IMAP.new(host)
  imap.login(user, password)
  imap.select("INBOX")
  imap.search(criteria)
  imap.uid_search(criteria)
  imap.sort(["DATE"], criteria, "UTF-8")
  imap.fetch(1, criteria)
  imap.disconnect
end

def unread_invoices(host, user, password)
  imap = Net::IMAP.new(host)
  imap.login(user, password)
  imap.examine("INBOX")
  imap.search(["UNSEEN", "SUBJECT", "invoice"])
end

def subject_search(rules_uri, host)
  subject = Net::HTTP.get(rules_uri)
  imap = Net::IMAP.new(host)
  imap.search(["SUBJECT", subject])
end
