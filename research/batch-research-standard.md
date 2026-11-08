# Systematic research standard for all eight Ghidra batches

**Purpose:** Turn a user-generated OrbusVR IL2CPP decompilation export into a public, AI-usable understanding of game systems. A 10,000-function index is only the start of a review, not proof that all 10,000 functions have been understood.

## The eight ranges

The full export contains **79,754 selected functions**, **79,745 successful decompilations**, **9 failures** and **400 text files**. One Ghidra-recognized count includes externals (79,943); the selected export excludes externals. One image base: `0x180000000`.

| Batch | Exported ordinals | Initial priority | Current research status |
|---|---|---|---|
| 1 | 1–10,000 | Native/IL2CPP foundation | Indexed; first overview published. Deep subsystem review not complete. |
| 2 | 10,001–20,000 | Networking, scene manager, NPCs | Indexed; receive parser, entity lifecycle, networking, scenes, NPC and class/HUD traces published; **not** exhaustively understood or runtime-tested. |
| 3 | 20,001–30,000 | Player, combat, items, world events | Indexed; multiple focused native behavioral traces published; **not** exhaustively understood. |
| 4 | 30,001–40,000 | Loot-menu and UI helpers | Index generated locally; deep review not yet published. |
| 5 | 40,001–50,000 | Gameplay dependencies and libraries | Index generated locally; deep review not yet published. |
| 6 | 50,001–60,000 | Unity support, rendering/transforms | Address scan exists; deep review pending. |
| 7 | 60,001–70,000 | Runtime and library code | Address scan exists; deep review pending. |
| 8 | 70,001–79,754 | Runtime and library code | Address scan exists; deep review pending. |

*Statuses are dated 2026-11-08 and should be updated whenever a report is actually published. The batch boundaries are Ghidra's function enumeration order, not logical class or namespace boundaries.*

## Required pipeline per batch

### 1. Integrity and input fingerprint

- Record exact archive/binary hashes and analyzed game build if known.
- Verify expected function ordinals, distinct VAs and Ghidra summary counts.
- Record all failed RVAs for a retry pass and differentiate timeout from subprocess launch failure.
- Do not commit proprietary game exports or decompiler pseudocode as a bulk archive.

### 2. Address-to-name linking

- Convert VA to RVA using the **actual Ghidra image base**, not guessed offsets.
- Join every matching function to `dump.cs` / `script.json` (and `il2cpp.h` when field layouts matter).
- Annotate multiple managed declarations that share an RVA (generic, shared, stub, thunk or method aliases); never assume one RVA = one distinct managed feature.
- Prefer precise managed names, signatures, type/namespace, and snapshot reference over anonymous `FUN_...` labels.

### 3. Build a call and state graph

- For each chosen entry point: inspect direct callers, direct callees, initialized fields, relevant object lifetimes, branching conditions and exception paths.
- Separate **local visuals**, **incoming replication**, **outgoing requests**, **server-authoritative state**, **persistence**, **UI** and **assets/scene streaming**.
- A direct-call scan cannot see all virtual/indirect/dynamic invocations. Label coverage accordingly.
- Avoid treating a numeric method ID as a global RPC command; identify component scope and receiver.

### 4. Explain behaviour, not only existence

A genuinely useful finding should answer:

1. **What triggers it?** (input, callback, UI, network event, scene lifecycle)
2. **What does it read/change?** (fields, GameObjects, Transform, inventory, serialized data)
3. **What else does it call?** (named chain with RVAs)
4. **Does the server own the result?** (client request vs replicated confirmation vs local-only state)
5. **What can a mod do with it?** (read-only telemetry, safe UI integration, hooks, admin server integration, asset capture)
6. **What must be tested?** (setup, expected result, failure path, build compatibility)

### 5. Check large and high-value methods

Do not stop after the first five named functions. Prioritize class constructors, network initializers, state machines and unusually large methods. However, a giant Ghidra function can be mostly compiler/IL2CPP boilerplate (for example Bard's constructor and SuperTextMesh rendering); **size is a clue, not a measure of game-specific value**.

### 6. Publish an AI-readable artifact

For each batch, add:

- **System pages:** independently written technical explanations grouped by gameplay domain.
- **Method index:** names, signatures, RVAs, references and tested status.
- **Call/field evidence:** addresses and qualitative branch conditions—not full raw pseudocode.
- **Modding recipes:** practical integration points, dependencies, and caveats; link working open-source source only after checking it.
- **Confidence and test plan:** label static analysis separately from actual tests.
- **Open questions:** do not silently fill in missing server or persistence details.

## Evidence labels

- **Mapped:** named by a specific IL2CPP metadata snapshot; no semantics proven.
- **Static-traced:** behavior supported by the decompiled control flow and related call sites.
- **Runtime-tested:** reproduced against a specific client/server build and recorded method/test result.
- **Inferred:** plausible implication, explicitly separated from observation.
- **Unresolved:** important functionality for which the current evidence is incomplete.

A function entry does **not** graduate from Mapped to Runtime-tested by being indexed. Reports must never present guesses as implementation-ready APIs.

## Batch 02 audit trail (first deep subsystem review)

- 10,000 functions; **9,999** successful Ghidra decompilations and **1** timeout at `0x30F330` (`OrbusNetManager..ctor()`).
- **29,432** distinct direct caller/callee relationships in the offline index, **22,034** within this batch.
- **120** selected managed method signatures mapped to **98** distinct RVAs. Important shared stub: `0x2F1730` appears under 19 selected managed names.
- [Deep review overview](export-batch-02-deep-dive.md), [incoming parser and entity factory](batch-02-incoming-message-parser-and-spawns.md), [component dispatch/despawn/remote movement](batch-02-component-dispatch-and-entity-lifecycle.md), [ENet/scene/prefab pools](batch-02-connections-zone-loading-and-prefab-pools.md), [NPC dialogue](batch-02-npc-dialogue-interaction-and-ui.md), and [Orbhealer/health bar](batch-02-orbhealer-healthbars-and-combat-ui.md).
- **Machine-readable curated signatures:** [`batch-02-curated-methods.json`](../references/batch-02-curated-methods.json).
- Still unresolved: server-side permission validation, entity-interest radius, full protocol framing, one timed-out constructor and runtime verification.

## Batch 03 audit trail (initial deeper pass)

- 10,000 functions; 9,996 decompiled; 4 failures.
- 465 previously curated game method signatures fall into this range (a *sample*, not the exhaustive symbol universe).
- 229 functions with 258 visible calls to `NetEntity.CallServerComponent`, catalogued automatically.
- Nine selected components, 64 explicit sync-variable or incoming-listener registrations.
- 27 high-interest named trace nodes extracted with same-batch direct callers.
- Dedicated topic guides cover: [player/camera/world](batch-03-player-camera-and-world.md), [network contracts](batch-03-server-and-network-contracts.md), [class mechanics](batch-03-combat-and-classes.md), and [items/events/UI/weapon adjuster](batch-03-items-events-ui-and-weapon-adjustments.md).
- Four unresolved decompiler RVAs: `0x4FFDE0`, `0x58B170`, `0x5930A0`, `0x5DFEB0`. One failed to start the Ghidra decompiler subprocess; the other three timed out.

**Still unresolved:** completeness of managed symbol joining, full callbacks and effects, server receiver implementations, and runtime reproduction. These are research to-do items, not already delivered features.

## Suggested remaining review order

1. **Batch 02** — follow [the new native parser/dispatch guide](batch-02-incoming-message-parser-and-spawns.md) to server interest management, receiver permissions and experimental validation; major client paths are now statically traced.
2. **Batch 04** — loot/presentation/PowerUI and inventories.
3. **Batch 05** — trace dependencies called from named class/scene systems.
4. **Batches 06–08 and 01** — tackle runtime/Unity internals selectively and document what they illuminate for actual Orbus gameplay.

The goal is not to manually paraphrase 80,000 function bodies or upload copyrighted sources. It is **a coherent system-level reference with reproducible traces, honest confidence labels and working implementation guidance**.
