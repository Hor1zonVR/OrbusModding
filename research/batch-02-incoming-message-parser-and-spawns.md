# Batch 02 — Incoming network message parser, entity spawning and component dispatch

**Static-traced game code:** `OrbusNetManager.ReadNextMessage(BinaryReader)` **RVA `0x30B690`**, Ghidra ordinal **19,815**, approximately 9.1 kB of native pseudocode. **Build:** private, unverified OrbusVR IL2CPP `GameAssembly.dll` snapshot. RVA relative to `0x180000000`. This is **research**, not a verified standalone protocol spec or a supported hook.

This page joins the parser to the networking and entity updates documented in [the component guide](batch-02-component-dispatch-and-entity-lifecycle.md). Most method names were **cross-checked against the matching managed-method dump**, rather than guessed from anonymous Ghidra names.

## The central parser

`OrbusNetManager.ReadNextMessage(BinaryReader reader)` is a large branching dispatcher. Its native body:

1. Checks the reader/underlying stream and obtains the next code (virtual reader method).
2. Recognizes an optional special value **`0x42`** as a flag/prefix in one branch (meaning to be established).
3. Routes certain code ranges to entity creation/update handling, and higher component-tagged codes to the listener/synchronized-variable path.
4. Handles named discrete cases for player initialization, other-player data, despawning, ping, text and several control/UI messages.
5. Returns a boolean indicating whether an inspected branch was handled; unknown cases can log and return false.

**Don't** equate these values with unframed UDP packets. They are values read from an already obtained `BinaryReader`; preceding transport framing/flags must be verified.

## Native branch-to-method map

| Reader branch / condition | Named target | RVA | Source evidence and cautions |
|---|---|---|---|
| Dynamic entity-update range, numerically tied to **10,000+ type codes** | `OrbusNetManager.handleEntityUpdate(ushort entityType, ushort entityGuid, bool forceDestroy, BinaryReader)` | **`0x31D400`** | Derives a type code, reads a GUID and forwards force-destroy state. Actual factory lookup happens in downstream handler. |
| Component-tagged range involving **30,000+ component IDs** | `NetEntity.TriggerListenerForMethod(string componentName,byte methodId,BinaryReader)` | **`0x2F3360`** | Reads entity GUID, resolves entity by GUID, resolves component name from manager mapping at `+0x398`, dispatches incoming component method/state. Outgoing `CallServerComponent` uses the same **30,000 offset scheme** in this snapshot. |
| `0x0C` (12) | `OrbusNetManager.initializePlayerRig(...)` | **`0x31EF50`** | Reads local player identity, three position components and four quaternion components; initializes/updates local rig, then calls `sendPing`. |
| `0x0D` (13) | `OrbusNetManager.handle...OtherPlayer...` (named mapping below) | **`0x31D7B0`** | The native path looks up or creates an `OtherPlayerEntity`, then calls `OtherPlayerEntityUpdateFromRemote(BinaryReader)` `0x32F7D0` (Batch 03). See separate section. |
| `0x23` (35) / `0x24` (36) | `OrbusNetManager.handleEntityDespawn(...)` | **`0x31D330`** | Two branches invoke same helper with distinct boolean mode; the significance of each mode beyond the argument requires testing. |
| `0x29` (41) | `OrbusNetManager.handlePing(BinaryReader)` | **`0x31DDC0`** | Distinct from the outgoing `sendPing` code that writes initial `0x28` (40). Underlying timing/latency response should be traced before claiming exact ping semantics. |
| `0x32` (50) | `OrbusNetManager.handleWsTextMsg(string)` | **`0x31E6B0`** | Reads incoming text and passes it to a separate message processor; potential chat/control/state multiplexing requires inspecting that handler. |
| `0x0B` (11) | `OrbusNetManager.UpdateDebugBox(ushort,BinaryReader)` | **`0x30E000`** | UI/debug updating path. |
| `0x41` (65) | native manager helper `0x307B60` | `0x307B60` | Needs further name/meaning confirmation before assigning a packet semantic. |

### Why this changes earlier interpretations

We previously knew `NetEntity.RegisterNetSyncVar` and `TriggerListenerForMethod` existed. Now we have **the actual parser that reaches them**, plus the branch that selects **entity type/GUID construction** rather than component callbacks. The 10,000 and 30,000 schemes are **context-dependent**; do not assume every code in a broad numeric interval is meaningful or valid.

## Entity update path — type, GUID, prefab and Transform

`OrbusNetManager.handleEntityUpdate(...)` **`0x31D400`**:

1. Resolves an existing `NetEntity` through `findEntityByGuid(ushort)` **`0x31CB60`**, which looks up a dictionary at `OrbusNetManager + 0x388`.
2. If the packet's replace/force-destroy flag applies to an existing entity, calls `NetEntity.Despawn(true)` **`0x2F2C70`** and removes that entity from **both** the active list `+0xA8` and GUID lookup `+0x388`.
3. Otherwise, if it needs a new entity, resolves a type/factory from manager dictionary **`+0x390`**, creates a `NetEntity`-like object through factory/constructor `0x2F49B0`, registers it in the GUID lookup and active list.
4. Reads **seven floating-point values** from the `BinaryReader` and calls `NetEntity.UpdatePositionFromRemote(...)` **`0x2F4540`**. These correspond to a 3-vector position and 4-component rotation in the matching managed signature.

This last call also resolves an ambiguity: Ghidra's standalone decompilation of `0x2F4540` infers an incomplete native parameter list, but the explicit call from `handleEntityUpdate` supplies the additional transform values. **Cross-check callers when Ghidra signatures look wrong.**

### Distinct other-player entity path

`OrbusNetManager.handle...` **`0x31D7B0`** (managed name below) handles a record specifically for another player:

- Finds an existing entity by GUID or despawns/removes it when a replacement flag is set.
- Uses an `OtherPlayerEntity` factory/constructor at **`0x3301E0`**, and adds it to the same active list and GUID dictionary.
- Calls **`OtherPlayerEntity.OtherPlayerEntityUpdateFromRemote(BinaryReader)` `0x32F7D0`** (Batch 03), rather than the generic seven-float positional update alone.

The Batch 03 method decodes multiple remote-avatar Transform groups. The per-frame `OtherPlayerEntity.UpdateObjectPosition(float)` **`0x32FDA0`** then interpolates and applies them.

**RebornCamera take-away:** the correct raw incoming data feed for a full-body remote replay is not `NetEntity` position alone. One packet path includes extra head/hand/body anchors. A party-synchronized replay design should record those, a stable session/instance identity and time alignment, while accounting for entity replacements.

## Despawn protection for the local player

`OrbusNetManager.handleEntityDespawn(ushort,BinaryReader,bool)` **`0x31D330`**:

- Returns early if the target GUID matches the current local player rig's ID at `OrbusNetManager + 0x60`.
- Otherwise finds the entity, checks an active-state byte (`NetEntity + 0x28`), invokes `NetEntity.Despawn(mode)`, removes it from the live list and GUID lookup.
- Returns if no active matching entity exists.

This proves that despawn handling is linked to the **same GUID collection and dictionary** as entity updates, but it does not establish the server's interest/culling policy or whether every object can be reloaded at will.

## Important unresolved items

- The exact managed signature/name of `0x31D7B0` is awaiting a dump cross-check; its control flow and direct call to `OtherPlayerEntityUpdateFromRemote` are visible.
- The meaning of the special `0x42` prefix/flag.
- Complete validation and framing of the component-coded ranges.
- Server interest management: **why** the server sends or omits an entity to a particular player.
- Whether a client's camera position influences the server's entity selection (not established by these methods).

## Reproducible private-server diagnostics

Observe one NPC/player entity as it enters, moves, switches zones and despawns. Log **only** its temporary entity ID, type, local timestamps, dispatcher branch, creation/replacement/despawn and Transform-availability flags; avoid player names or auth tokens. Test with an actual consenting remote player to check the richer other-player record.

**Static result:** the parser → entity factory → transform-update → frame-render pipeline is now mapped. **Runtime result:** not yet tested. Never claim this is a supported external server command protocol.
