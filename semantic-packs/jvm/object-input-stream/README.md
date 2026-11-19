# Reviewed ObjectInputStream constructor summary

`bifrost.jdk-object-input-stream-summaries` holds one hand-reviewed procedure
summary, for the JDK constructor `java.io.ObjectInputStream(InputStream)`. It
exists for the `bifrost.security.java.objectinputstream-read-without-filter`
typestate policy (BrokkAi/bifrost-dev#14542).

The summary states two facts from the Java SE API specification:

- An `allocation` effect whose output is `normal_return`. Each call returns a
  new stream object, so the engine treats the constructed stream as a fresh
  typestate subject. Only a fresh subject lets the engine prove that an
  unmodeled call, or a second stream, cannot reach it before `readObject()`.
- A transfer from parameter 0 to the result, a `conversion` with
  `preservation: changing`. The stream reads its bytes from the wrapped input,
  so taint on the input still reaches the stream. The stream is a different
  object from its input, so the transfer is not `identity`; an identity
  transfer would also conflict with the allocation.

The summary does not claim `ordinary_heap_unchanged`: the constructor reads
the stream header from the input, which advances it.

The target is matched by artifact path and signature, like the generated
`bifrost.jdk` declarations, so the pack applies on every JDK from 17 on. The
member IDs that the policy selects are the same on JDK 17.0.16 and 21.0.8.

The generated `bifrost.java-codeql-jdk-summaries` pack carries a plain
parameter-to-return transfer for the same constructor and no allocation. That
pack is source-only and generated from CodeQL, so the reviewed fact lives
here instead.

Needs a Bifrost engine that contains BrokkAi/bifrost-dev#14546. Older engines
look up constructor summaries with a receiver and do not treat the allocation
root as the result's identity, so the summary changes no typestate result
there.
