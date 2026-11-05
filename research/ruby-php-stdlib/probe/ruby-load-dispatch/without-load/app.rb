class LocalCodec
  def self.decode(bytes)
    bytes
  end
end

def other(x)
  Marshal.dump(x)
end

def workspace_call(bytes)
  LocalCodec.decode(bytes)
end
