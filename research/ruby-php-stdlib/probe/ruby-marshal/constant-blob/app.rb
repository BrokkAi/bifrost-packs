BLOB = "\x04\b[\x00".b

def defaults
  Marshal.load(BLOB)
end
