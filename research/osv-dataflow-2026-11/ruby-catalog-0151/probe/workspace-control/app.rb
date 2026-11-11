class Mailbox
  def fetch(set, attr, changedsince: nil)
    [set, attr, changedsince]
  end

  def cap=(value)
    @cap = value
  end

  def [](index)
    index
  end
end

def run(attr, since, i)
  box = Mailbox.new
  box.fetch(1, attr)
  box.fetch(1, attr, changedsince: since)
  box.cap = since
  box[i]
end
