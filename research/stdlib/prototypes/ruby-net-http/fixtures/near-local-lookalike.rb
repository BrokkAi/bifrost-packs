class HTTP
  VERIFY_NONE = 0

  attr_accessor :use_ssl, :verify_mode

  def initialize
    @use_ssl = false
    @verify_mode = nil
  end

  def start
    yield self
  end

  def get(_path)
    :response
  end
end

def local_lookalike(path)
  http = HTTP.new
  http.use_ssl = true
  http.verify_mode = HTTP::VERIFY_NONE
  http.start do |active_http|
    active_http.get(path)
  end
end
