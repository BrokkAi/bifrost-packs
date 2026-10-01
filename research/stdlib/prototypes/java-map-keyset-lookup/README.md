# Java Map keySet/get repeated-lookup qualification

Status: **discovery only; no rewrite policy is qualified**.

This prototype asks whether a Java loop iterating Map.keySet() performs a
repeated Map.get(key) that is safe to replace with entry iteration. No
performance benefit is claimed. A performance claim requires a separate
profile against a pinned baseline and benchmarked revision.

A reportable optimization must prove all of the following from analyzer
evidence:

- exact JDK Map.keySet() and Map.get(Object) declarations and a closed
  dispatch set that accounts for overrides;
- the same stable receiver/object for iteration and lookup, including proven
  aliases where supported;
- the same loop-key binding at the lookup, with no intervening reassignment;
- containment in the same executable declaration and the same loop;
- no map mutation or unresolved effect that can change the lookup result; and
- a supported map contract that excludes custom overrides with observable
  get behavior.

The authored Java fixture covers the direct positive shape and controls for
key-only iteration, entrySet, a different map, a get outside the loop in the
same declaration, a nested loop with a different key, changed loop key,
mutation, unknown callback effects, receiver reassignment, aliasing, a custom
get override, and a local lookalike type. These are analyzer inputs only; no
runtime or benchmark execution is intended.

The saved CodeQueries use inside for the actual for_loop region. Separate
binding-of queries expose stable lexical binding ids for the receiver
occurrences, so the direct same-map positive and different-map control can be
compared by ID. For the get argument, binding-of does not return a stable row.
The raw occurrence result labels the target as an enhanced-for variable and
provides its name and source range, but no stable target ID. This is not enough
to prove that the get argument and loop binder share a binding. The nested-key
case therefore remains a discovery candidate. These queries also do not
establish heap aliasing, closed virtual dispatch, or complete effects. The
state-event probes retain local reassignments; unsupported effect or flow axes
remain explicit. call-sites-from and receiver analysis are also preserved as
probes, including their incomplete outcomes.

The RQLP file is a note-only structural prompt. It is not listed in a shared
manifest or policy catalog, and it is not suitable for scanner activation.

## Observed capability boundary

With the pinned Bifrost 0.12.0 binary, the active generated JDK 21.0.8 model
provides exact model identities for Map.keySet() and Map.get(Object), plus
exact receiver/argument mapping rows. Those model records are partial; calls
through a Map receiver report selector_exact false, dispatch_outcome unproven,
and dispatch_coverage open. The golden-core procedure summaries for both
methods are partial with no listed effects, which cannot establish purity. The
RecordingMap.get override control therefore remains unresolved at a Map-typed
call.

The same pinned run resolves the local lookalike calls to source declarations
with exhaustive dispatch, showing that the unrelated methods are distinguishable.
The direct Java binding queries prove receiver-binding equality for the
straightforward positive fixture. The missing stable ID for the enhanced-for
key is a separate Java CodeQuery binding-publication gap. Lexical receiver
equality does not establish object identity for aliases or rule out mutation
through calls.

These findings are on the pinned 0.12.0 artifact only. They do not establish
that current Bifrost source is defective. Existing upstream capability trackers
are #3811 for Java external dispatch/binding completeness, #2444 for bounded
alias/object identity, and #2445 for complete behavior/effect summaries. The
separate stable enhanced-for binding-row gap is tracked in
[bifrost-dev#3814](https://github.com/BrokkAi/bifrost-dev/issues/3814).

## Reproduction and provenance

Run scripts/replay.py with the pinned Bifrost binary. It writes raw JSON
responses, stderr, input/output SHA-256 digests, model identities, policy
completion, and binding comparisons under evidence/replay/. The default
binary SHA-256 pin is recorded in the script and receipt.json.

The discovery query is structural. The additional binding, call-site,
receiver, state-event, and flow queries keep resolver proof and typed
incompleteness visible. An empty set under partial analysis is not evidence of
safety.

## Performance evidence

No profile or benchmark was run. The transformation has no claimed speedup.
