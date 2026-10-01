require 'net/http'
require 'openssl'

def request_with_peer_verification(host, path)
  http = Net::HTTP.new(host, 443)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_PEER
  http.start do |active_http|
    active_http.get(path)
  end
end
