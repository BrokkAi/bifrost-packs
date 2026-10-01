require 'net/http'
require 'openssl'

def configure_but_never_start(host)
  http = Net::HTTP.new(host, 443)
  http.use_ssl = true
  http.verify_mode = OpenSSL::SSL::VERIFY_NONE
  http
end
