# Sensitive source role audit

The variable source uses structured identifier occurrences in the value
namespace. It includes both runtime expression-read roles, including the
receiver in `password.as_str()`. All include and exclude name predicates use
the same role set; a sensitive receiver cannot bypass name exclusions.

| Occurrence role | Variable source | Reason |
| --- | --- | --- |
| `value_reference` | include | Ordinary expression value accesses, including qualified terminal values. |
| `receiver_position` | include | A receiver is a value read, even when used to call a method. |
| `member_position` | exclude token | Member labels are not local-variable reads. Actual field expressions are handled by the field source; sensitive calls by their result source. This avoids treating initializer and pattern field labels as values. |
| `declaration_name` | exclude | Declares a name rather than reading its value. |
| `binder` | exclude | Parameters, locals and pattern introductions are not reads. |
| `label_or_key` | exclude | Labels and keys do not read the named variable. |
| `type_operand` | exclude | A type expression does not read a runtime value. |
| `path_segment` | exclude | Non-final Rust qualifiers identify modules/types, not runtime variable reads; the terminal expression inherits its expression role. |
| `import_alias` | exclude | An import alias introduces a name. |
| `import_target` | exclude | Import syntax does not read the imported value at runtime. |
| `pattern_position` | exclude | Pattern/type selection is not a variable-access expression. Pattern binders remain excluded separately. |
| `generated_source` | exclude | Not a runtime read; this role is unsupported by the Rust adapter. |
| `global_directive` | exclude | Python directive, unsupported by the Rust adapter. |
| `nonlocal_directive` | exclude | Python directive, unsupported by the Rust adapter. |

The field source selects whole `field_access` expressions, not field-name
occurrences. Its `matched-value` binding covers the sensitive field value
when it is itself a receiver, as in `self.api_key.inner()`, and in ordinary
expression positions. Declaration heads, constructor field keys and pattern
field labels are not `field_access` expressions. It has no occurrence-role
filter to suppress receiver uses. Recursive parent-field source coverage is
still a documented engine limitation.

The call source selects whole `call` expressions by structured callee names
and binds `return-value`. It remains a source when its result is consumed by
another call or used as a receiver. The call entry binds results rather than callee tokens. A plain callee token
may have `value_reference` role; the variable selector does not claim a
resolved variable-versus-callable declaration-kind guard from that role alone.
Semantic binding remains necessary. CodeQL's resolved
Function/Variant target guard remains the documented source coverage
limitation; this change does not claim to add it.

Occurrence roles classify syntax rather than prove flow or access modes.
Value-reference roles can include writes; semantic matched-value binding and
the taint witness remain necessary. This audit does not convert an incomplete
binding or procedure proof into a clean or definite result.
