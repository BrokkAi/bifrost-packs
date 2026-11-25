package oisunknown;

import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;
/** Inert escape case for BrokkAi/bifrost-packs#301. */
public class Escapes {
    /** Unknown: a helper may or may not set a filter before the read. */
    public Object configuredElsewhere(InputStream in) throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(in);
        configure(ois);
        return ois.readObject();
    }

    private static void configure(ObjectInputStream ois) {
        ois.setObjectInputFilter(ObjectInputFilter.Config.createFilter("ois.Dto;!*"));
    }
}
