require "net/http"
require "yaml"

class LocalCodec
  def self.decode(bytes)
    bytes
  end
end

def stdlib_calls(uri, text, cmd)
  body = Net::HTTP.get(uri)
  Marshal.load(body)
  Marshal.restore(body)
  Psych.unsafe_load(text)
  YAML.unsafe_load(text)
  Kernel.open(cmd)
  open(cmd)
  Kernel.eval(text)
  eval(text)
  File.open(cmd)
end

def workspace_call(bytes)
  LocalCodec.decode(bytes)
end
