require 'net/http'
require 'openssl'

def weak_config_on_inactive_object(host, path)
  weak = Net::HTTP.new(host, 443)
  weak.use_ssl = true
  weak.verify_mode = OpenSSL::SSL::VERIFY_NONE

  active = Net::HTTP.new(host, 443)
  active.use_ssl = true
  active.start do |active_http|
    active_http.get(path)
  end
end
