# Ruby core collection element-access model

`ruby-core-collections.json` (`bifrost.ruby.core-collections`) declares `Hash`
and `Array` with `new`, `[]`, `[]=` and `fetch`. It also carries complete
summaries with no effects:

- **Reads** pass the receiver to the result.
- **Writes** pass the value into the receiver and to the result, and do not
  claim that the heap is unchanged.
- **Constructors** that take an argument pass it to the result, so
  `Array.new(array)` keeps the copied flow.

`dig` is not modeled, because it calls `dig` on the nested values.

The engine binds these members only where it can prove the receiver's class.
From Bifrost 0.15.3 on, that covers:

- hash and array literals;
- `Hash.new`/`Array.new` locals;
- parameters typed by an inline Sorbet `sig` or by a workspace `sig/*.rbs`;
- parameters whose callers all pass a proven literal or constructed collection.

Element access on an untyped receiver stays incomplete. `[]` there could be
`Proc#[]`, `Method#[]`, `Struct` or a user-defined method.

The ids follow two rules. Type ids are the canonical
`type_declaration_id(rubygems, name)`; the engine finds `Hash` and `Array` by
nothing else. Member and summary ids are distinct. A reused id makes discovery
refuse the whole workspace model directory.

## Accepted residual: implicit callbacks

`Hash#[]`, `Hash#fetch` and `Array#[]`/`[]=` can run user code that these
summaries do not represent:

- a default proc, from `Hash.new { ... }` or a later `default_proc=`;
- a key's `hash` and `eql?` methods;
- an index's `to_int`.

Such code can perform effects or produce the returned value. The summaries
still claim complete and effect-free. The owner accepted this residual on
2026-11-17.

Two cases stay open anyway:

- **Block-form `Hash.new { ... }`:** the call stays incomplete, so a default
  block that reaches the network keeps the run open.
- **`default_proc=`:** it is not modeled, so a call to it stays incomplete.

`covers_overrides` is `true`, as in the reviewed `Net::HTTP` model. With
`false`, even exact literal receivers stop closing. A workspace subclass that
overrides `[]` still leaves dispatch unproven.
