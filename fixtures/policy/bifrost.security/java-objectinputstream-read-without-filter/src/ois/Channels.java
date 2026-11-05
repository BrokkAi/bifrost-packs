package ois;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;
/** Inert ObjectInputStream filter cases for BrokkAi/bifrost-packs#301. */
public class Channels {
    /** Positive: caller bytes read with no filter (the CVE-2026-41586 shape). */
    public Object deserialize(InputStream in) throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(in);
        return ois.readObject();
    }

    /** Positive: construction and read in one expression. */
    public Object deserializeChained(InputStream in) throws IOException, ClassNotFoundException {
        return new ObjectInputStream(in).readObject();
    }

    /** Positive: the filter is set only after the first read. */
    public Object filterTooLate(InputStream in, ObjectInputFilter filter)
            throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(in);
        Object first = ois.readObject();
        ois.setObjectInputFilter(filter);
        return first;
    }

    /** Near miss: a filter is installed before the first read. */
    public Object deserializeFiltered(InputStream in, ObjectInputFilter filter)
            throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(in);
        ois.setObjectInputFilter(filter);
        return ois.readObject();
    }

    /** Near miss: the stream is created but never read. */
    public ObjectInputStream openOnly(byte[] bytes) throws IOException {
        return new ObjectInputStream(new ByteArrayInputStream(bytes));
    }
}
