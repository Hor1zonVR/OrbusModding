# Batch 03 — Combat classes, gesture systems, feedback and replication

**Source:** Decompiled `GameAssembly.dll` functions, linked to type/method declarations in the user's matching IL2CPP dump. **Build:** not positively identified. **Confidence:** native static control-flow analysis unless stated otherwise. Addresses refer to RVA from image base `0x180000000`.

These notes are intended for gameplay mod authors, combat logger/overlay authors, and researchers creating new abilities. The most important pattern is to distinguish **input**, **visual presentation**, **outgoing request**, **confirmed game state** and **server-side effect**.

## Runemage — gestures are not the same as successful casts

Relevant path:

| Method | RVA | Responsibility supported by static inspection |
|---|---|---|
| `Runemage.prepareSpellCast(int)` | `0x47E8A0` | Stores selected spell ID (field around `+0x148`), updates trigger/gesture graphics, and has a special early branch when the ID is **99** (sentinel/no recognized spell). |
| `Runemage.finishSpellCast()` | `0x47D830` | Completes a sequence of gesture-point operations, constructs a request if the derived point set is nonempty, calls the class network component's method **1**, then clears its spell-line state. |
| `Runemage.resetSpellLines()` | `0x47EB80` | Clears/discards client-side drawn spell lines; does not establish that any cast succeeded. |
| `Runemage.orbusNetInit(NetEntity)` | `0x47E410` | Registers six net-sync indices and four incoming method listeners (IDs 1,2,3,5). |
| `Runemage.doPadClick(...)` | `0x47CC60` | One of four visible direct callers of `finishSpellCast`. |
| `Runemage.doPrimaryTriggerClick()` | `0x47CE60` | Another direct caller; other caller RVAs are `0x47CE00` and `0x47D130`. |

`finishSpellCast` reads current stroke/gesture buffers and builds an outgoing serialized candidate. The Ghidra code checks that there is at least one populated element before sending. It marks a client-side state flag around `+0xC9` before the outgoing request. Neither that flag nor the presence of method-ID 1 proves that the server accepted the spell or that a target was hit.

**For a reliable CPS/DPS mod:** report four distinct counters: (1) strokes completed, (2) client requests submitted, (3) acknowledged or combat-log-confirmed successful casts, (4) server-derived damage/healing. Avoid calling each request a success. To determine timing windows, inspect `finishSpellCast` together with gesture recognizer setup and incoming methods, then test with deliberately wrong shapes.

## Bard — note matching, private rolling song buffer and network submission

| Method | RVA | Observed path |
|---|---|---|
| `Bard.RegisterNoteHit(int,GameObject)` | `0x41EFC0` | Searches a local list of registered note/instrument objects for the hit GameObject; prepares a record with default note index **99** and a secondary byte, then conditionally sends class method **4** if the corresponding note slot is enabled. |
| `Bard.AddNoteToHiddenSong(int)` | `0x41BFC0` | Appends note IDs to a list at approximately `Bard + 0x2A0`. When the list exceeds **10 entries**, removes the oldest. It checks the suffix against a fixed target-sequence array at about `+0x2A8`; when matched, a separate action/effect is invoked. |
| `Bard.FixedUpdate()` | `0x41CC20` | Has **two direct code-site invocations** of `AddNoteToHiddenSong`, making it an important entry point for investigating how recorded notes are assembled. |
| `Bard.UpdateBeltOrbs()` | `0x420EC0` | Orb appearance/state maintenance path; exact server-side buff values must be separately confirmed. |
| `Bard.UpdateNotchedOrbs()` | `0x421670` | Related instrument/orb view refresh. |
| `Bard.orbusNetInit(NetEntity)` | `0x427930` | Registers seven synced-variable slots and incoming methods **1,2,3**. |
| `Bard..ctor()` | `0x4227D0` | A very large (~209 kB decompiled) initializer containing arrays and class data. Large decompiled size is partly repeated IL2CPP array-guard boilerplate, **not proof** of advanced combat logic or numerical buff rules. |

**Potential community feature:** a read-only Bard note/song diagnostic that records accepted note-object matches and sliding sequence-match states. This would be useful for teaching songs and verifying whether orb effects correspond to the expected notes. Before displaying exact buff percentages, derive them from server status changes, incoming sync callbacks or an authoritative server definition—not just note VFX.

**Caveat:** the rolling queue's size is evidenced by append → if count > 10 then remove first; the target sequence's semantics and resulting action remain to be validated. Do not call it a hidden cheat or special ability without a runtime test.

## Shaman — visual orb creation is distinct from spawning an authoritative totem

- `Shaman.SpawnOrb(int slotNum,byte spellid)` **`0x485830`**: replaces a local orb GameObject/prefab in a specified slot and updates its local appearance and positioning. This is **presentation code**, not by itself a server request to grant the spell.
- `Shaman.SpawnTotem(byte spellId,Vector3 position)` **`0x485CA0`**: packs spell ID and a 3-component position, then sends **Shaman component method 1** via `NetEntity.CallServerComponent`.
- `Shaman.orbusNetInit` **`0x488A80`**: registers **five** synced-variable indices and **one** incoming method listener.

This split suggests two diagnostic milestones for modders: local orb shown versus confirmed totem created. The exact network validation, mana/charges, position constraints and expiration remain unknown.

## Monsters — replicate status, render attacks, do not infer client authority

`Monster.orbusNetInit()` **`0x5B6080`** registers net-sync indices **1–13** and incoming listener IDs **1, 5–12, 14**. The incoming callbacks contain important visual/combat feedback:

- `Monster.<orbusNetInit>b__14` **`0x5B7F10`**: visual telegraph spawn, including shapes and time-limited effects.
- `Monster.<orbusNetInit>b__15` **`0x5B8740`**: incoming damage/heal feedback and source identifiers for client presentation.
- `Monster.<orbusNetInit>b__16` **`0x5B8EF0`**: casting-bar duration/animation presentation.
- `Monster.<orbusNetInit>b__17` **`0x5B9260`**: cancel-casting presentation.
- `Monster.<orbusNetInit>b__18` **`0x5B9310`**: name-matched VFX instantiation and temporary lifetime.
- `Monster.showTelegraph(...)` **`0x5B6CE0`**: creates/scales an attack telegraph and schedules cleanup.
- `Monster.showSphereTelegraph(...)` **`0x5B6B30`**: creates a sphere telegraph using **diameter = 2 × radius** for visual scale and schedules cleanup.
- `Monster.UpdateStatusEffect(...)` **`0x5B5780`**: local status-effect model/display update pathway; examine it before drawing authoritative conclusions about effect stacking or damage.

**Best use:** a diagnostic/overlay subscriber that observes incoming visual damage and cast state, correlates it with the combat log, and marks gaps. A mod that merely changes client hitpoints or telegraph VFX should not claim to alter the actual server damage mechanics.

## Fisher — separate other-player presentation path

- `Fisher.orbusNetInit()` **`0x412000`** registers one synced-variable index and incoming method IDs **1–5**.
- `Fisher.updateFishingLineOtherPlayer()` **`0x413060`** operates on other-player fishing visual elements; its observed path reads the pole/bobber transform positions and invokes a line renderer helper, with fallback to `UpdateLineRenderer`.
- `Fisher.updateFishingLine()` **`0x413200`** is a separate local path.
- `Fisher.showCatchReward(ushort,float,bool)` **`0x412600`** is a complex visual/result path (about 13.7 kB of pseudocode) that creates/updates reward display elements. We have not determined whether the float is sent over the network, calculated locally, or backed by a server transaction in all cases.

**Practical implication:** other-player visual equipment/line state can have a dedicated representation method; a generalized replay system should not assume all specialized equipment is recoverable from a single avatar Transform.

## Testing matrix for the community

| System | Safe test | What to log | What it validates |
|---|---|---|---|
| Runemage | Deliberate correct vs. incorrect gestures | Stroke count, outgoing cast request, combat-log result | Recognized attempts vs. accepted casts |
| Bard | Play known note sequences on private test character | Hit object, matched index, rolling 10-note window, outgoing note request | Local song recognition and submission |
| Shaman | Summon valid and intentionally invalid-position totems in a test world | Orb slot visual, outgoing request, replicated totem appearance | Visual effect vs. authoritative creation |
| Monster | Trigger telegraph/cast cancellation in a controlled fight | Incoming listener, visual instantiate/destruction, combat log | Telemetry fidelity |
| Fisher | Two test players fish at different distances | Remote-line renderer, avatar detail, bobber GameObject state | Specialized remote equipment capture |

**What is not yet known:** precise Bard buff percentages, server spell damage formulas, cast acceptance conditions, status-stack priorities, and ability cooldown authority. Do not publish guessed numbers as game facts.
