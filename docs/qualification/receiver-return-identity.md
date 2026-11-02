# Receiver-return identity review

The source pack `bifrost.jdk-golden-summaries` 0.2.1 classifies fourteen
normal-exit receiver-to-return transfers as identity conversions. This is a
patch correction to existing summaries under the release versioning guidance.
Pack IDs, summary IDs, activation, dependency scope and completeness are retained.
Partial summaries remain partial. This source-only correction does not select
these summaries for a native release or change the independent release versions.

The classification uses the existing authoring vocabulary:

```json
"value_transfer": {
  "kind": { "kind": "conversion", "preservation": "identity" },
  "operation": { "kind": "none" }
}
```

`none` supplies no separately selected implicit conversion operation. Identity
means that the normal result denotes the receiver object itself. It does not
follow from taint dependence, receiver mutation, equal values, or a shared runtime
class. Unclassified transfers retain their existing taint semantics.

## Reviewed identity returns

The linked Java SE 21 return contracts explicitly identify the receiver.

| Receiver and method | Overloads present | Return contract |
| --- | --- | --- |
| [StringWriter.append](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/StringWriter.html#append(java.lang.CharSequence)) | `CharSequence` | This writer |
| [StringBuffer.append](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuffer.html#append(java.lang.Object)) | `Object`, `String` | A reference to this object |
| [StringBuilder.append](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html#append(char)) | `char`, `char[]`, `int`, `CharSequence`, `Object`, `String` | A reference to this object / this Appendable |
| [StringBuilder.insert](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html#insert(int,java.lang.Object)) | `(int,Object)`, `(int,String)` | A reference to this object |
| [StringBuilder.replace](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html#replace(int,int,java.lang.String)) | `(int,int,String)` | This object |
| [StringBuilder.reverse](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html#reverse()) | `()` | A reference to this object |
| [StringJoiner.add](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/StringJoiner.html#add(java.lang.CharSequence)) | `CharSequence` | A reference to this StringJoiner |

## Reviewed exclusions

String transformations, Buffer-to-string conversion and Python string/bytes
transformations remain unclassified. Their contracts describe resulting values,
copies or conversions; they do not guarantee the receiver object for all inputs.
In particular, [String.trim](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html#trim())
returns the receiver only under a condition. Views, iterators, extracted elements,
streams, writers obtained from another object, and database result objects also
remain unclassified.

The reviewed source snapshot contains no receiver-to-return summaries for the
ECMAScript collection mutators `Array.prototype.sort`, `reverse`, `fill`,
`copyWithin`, `Map.prototype.set`, or `Set.prototype.add`. No new summaries are
introduced by this correction. There are likewise no StringBuilder delete,
deleteCharAt or StringBuffer insert/replace/reverse candidates in this snapshot;
`setLength` returns void and cannot establish result identity.

## Compatibility

The classification is accepted by the published v0.12.0 authored schema and its
compiler, and by the public 0.14.0 producer pinned in `native-generation.json`.
It uses existing fields and variants, requiring no new schema or consumer gate.
The v0.12.0 engine does not use this classification to derive receiver-result
identity; a consumer that enforces classified identity can distinguish these
reviewed returns from the unclassified cases.
