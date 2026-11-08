# Batch 03 — Networking, authority boundaries and component requests

**Source:** Ghidra-exported native pseudocode for function ordinals 20,001–30,000, cross-checked against a matching `dump.cs` snapshot. Image base `0x180000000`; game build unverified. **Evidence status:** static analysis only, not a confirmed server protocol specification.

## What the batch-wide call audit found

A query of all 10,000 indexed function bodies found **229 distinct native functions** containing **258 syntactically visible invocations** of `NetEntity.CallServerComponent` (**RVA `0x2F2910`**, Batch 02). These are *call sites*, not proof of 258 unique network actions, wire packets, or executable server endpoints. Some functions contain multiple branches; indirect calls are not included. The helper's source and behavior need to be confirmed against the matching native image.

For nine selected game components, scanning their `orbusNetInit` implementations found **64 explicit registrations** of either `RegisterNetSyncVar` (`0x2F3020`) or `RegisterListenerForMethod` (`0x2F2EF0`). The registration records and outgoing request call sites are available in the companion local metadata tables generated from the full index.

## Fundamental distinction: three paths, not one

1. **Client-initiated request:** A method constructs a class-specific payload, then calls `NetEntity.CallServerComponent(entity, componentName, methodId, payload)`. A send does **not** establish server acceptance.
2. **Synchronized variable:** `orbusNetInit` registers a per-component indexed variable with a callback that applies replicated state.
3. **Incoming component method listener:** `orbusNetInit` registers a method ID and argument schema to invoke a local callback when data is received.

**Numeric IDs are scoped to their component**: `Runemage` method 1, `Shaman` method 1, and `PlayerCharacter` method 1 are unrelated contracts. Treating a numeric method ID as a global command is incorrect.

## PlayerCharacter requests confirmed from native send sites

| Native method | RVA | Component method ID | What the code actually prepares |
|---|---|---:|---|
| `teleportPlayer(...)` | `0x38F5A0` | **1** | Destination position and rotation plus movement-state logic; also mutates the local player's transform. This is not an administrative teleport permission. |
| `InventoryMove(...)` | `0x37E370` | **5** | A new request object with source/destination 16-bit slot indices, one 16-bit container GUID/value, and two container-kind codes interpreted from type strings (observed codes 0–3). |
| `updateServerHandState(...)` | `0x390200` | **11** | Two 32-bit values (hand index/state). |
| `DoLoot(ushort)` | `0x378800` | **12** | 16-bit target GUID; queues a component request and plays a local GUI sound. It does not directly create inventory items. |
| `setHandTeleporting(...)` | `0x38E9E0` | **23** | Builds a hand selector after checking controller/character state and forwards it conditionally. |
| `SendSignalToTool(byte,ushort)` | `0x382280` | **28** | One-byte selector plus 16-bit signal ID. |
| `SummonMount()` | `0x384FD0` | **60** | Issues a player-entity mount request when the entity exists. |
| `Dismount()` | `0x378590` | **61** | Sends a distinct request for dismount; server acceptance and subsequent avatar state should be observed. |

These IDs are **static native send sites**, not a verified documented public client/server protocol. Even if packet sizes are inferable from object fields, the exact serialized representation requires confirming the serializer and receiver.

## Tool interactions — an end-to-end native trace

`DungeonShard.UseShard()` **`0x402CC0`**  
→ `PlayerTool.SendToolSignal(ushort)` **`0x3A60B0`**, with signal **1**  
→ `PlayerCharacter.SendSignalToTool(byte,ushort)` **`0x382280`**  
→ `NetEntity.CallServerComponent` **`0x2F2910`**, player component method **28**.

The `PlayerTool` wrapper checks a locally controlled avatar. It chooses a one-byte tool selector based on one of two recognized tool strings (values 1/2) or a default (0). The shard method also releases the grip/controller object if a held-tool condition is met. We have **not** established the server's shard-consumption behavior or validity checks.

Other direct same-batch callers of `PlayerTool.SendToolSignal` include functions at `0x3B89E0`, `0x3B8D90`, `0x3CA670`, `0x3F4C40`, `0x42A8E0`, `0x42B270`, `0x42B3C0`, `0x4440C0` and `0x488D70`. These are leads, not identified tool effects.

## Examples of class-specific outgoing requests

| Component | Calling method | RVA | Local method ID | Scope of claim |
|---|---|---|---:|---|
| `Runemage` | `finishSpellCast()` | `0x47D830` | 1 | Sends serialized candidate spell gesture data when required conditions are met. |
| `Bard` | `RegisterNoteHit(...)` | `0x41EFC0` | 4 | Sends matched note/instrument data after local checks. |
| `Shaman` | `SpawnTotem(byte,Vector3)` | `0x485CA0` | 1 | Sends a spell/totem identifier and world position. |

**Analytics caveat:** entering an outgoing method is not a reliable signal for a successful spell, buff or damage event. Confirm from server responses or combat outcomes.

## Component replication maps (explicit registrations)

| Component | `orbusNetInit` RVA | Synced variable indices | Incoming method listener IDs |
|---|---|---|---|
| `Monster` | `0x5B6080` | 1–13 | 1, 5, 6, 7, 8, 9, 10, 11, 12, 14 |
| `Bard` | `0x427930` | 1–7 | 1–3 |
| `Runemage` | `0x47E410` | 1–6 | 1, 2, 3, 5 |
| `Shaman` | `0x488A80` | 1–5 | 1 |
| `Fisher` | `0x412000` | 1 | 1–5 |
| `BossChest` | `0x42C7B0` | 1, 2 | none in this init function |
| `DynamicEvent` | `0x404340` | **1–5** | none visible in this init function |
| `PortalEventNetComponent` | `0x3ABA30` | **6** | none visible in this init function |
| `DungeonBarrier` | `0x4026E0` | **1** | none visible in this init function |

A registration declares interest in a slot/callback; it does **not** tell us the field's high-level meaning until the callback and state serializer are traced. A listener ID can be skipped/reserved (e.g., Monster's 13).

## How GameMaster authors should use this

**Legitimate design:** build authorized admin operations on the private server itself; use the discovered client protocol to understand how ordinary game interactions are represented, then verify how the server enforces them. Do not assume that an existing client request can set player level, spawn arbitrary gear, edit persistence or bypass permissions. The client `DoLoot` method is a request, not an item grant function.

**Read-only diagnostics pattern:** trace component name, ID, payload *type/size* (not sensitive player data) and server response outcomes in a controlled game instance. Correlate by timestamp and entity GUID. Strip or anonymize player identifiers in public logs. For class events, record attempted send, incoming confirmation and inventory/combat result separately.

## Unknowns and next steps

- **Batch 02:** inspect `NetEntity.CallServerComponent`, listener dispatch, entity update and `OrbusNetManager` packet construction before describing the wire protocol.
- **Server source:** identify the actual receiving handler, validation, permissions, persistence and rollback for every action.
- **Full method coverage:** the 229-function call-site list must be joined with the complete managed-method dump, not only the 585 curated symbols; otherwise many caller methods remain anonymous.
- **Runtime:** capture one permitted action per contract on a private server and compare the outgoing request with the server-state change.

A numeric packet ID is never sufficient evidence for a mod feature on its own.
