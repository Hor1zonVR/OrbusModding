# Batch 02 — First native network and scene-loading traces

**Stage:** targeted deep research into dependencies referenced by Batch 03; **not a complete review of Batch 02's 10,000 functions**. **Date:** 2026-11-08. **Source:** matching user-generated Ghidra export and IL2CPP metadata. **Build:** unverified, image base `0x180000000`. All claims below are *static tracing* unless stated otherwise.

## A. `NetEntity.CallServerComponent` message construction

**RVA `0x2F2910`**, exported ordinal **19,588**.

This method is directly invoked by hundreds of game-specific callers elsewhere in the code. The Batch 03 native scan identified **229 caller functions / 258 visible call sites** that use it. Here is the relevant *execution sequence* in the Batch 02 native function:

1. Constructs a temporary writer/serializer object and an output stream.
2. Uses a component-name argument and a `NetEntity`-related lookup (`0x31CC80`) to resolve a component-specific short identifier.
3. **Adds 30,000** to that derived short value before writing it into the outgoing stream. This is an observed offset in the native code, **not yet a documented packet type specification**.
4. Writes the supplied **one-byte method ID**.
5. Writes a **16-bit entity identifier** from the entity object (field at `NetEntity + 0x10`).
6. If a non-null payload object was provided, it passes that object into the configured serializer.
7. Obtains the encoded data and sends through one of two native transport code paths depending on a network-manager state field (notably a comparison with state `2`).

### Important consequences

- The request is not identified solely by its method number. At minimum, it also involves a **component identity** and **entity identity**.
- The observed **+30,000** is part of a client-side wire-envelope construction step; it is not a universal claim about server packet IDs or permissions.
- This method shows **how a request is serialized**, not whether the server accepts it or persists changes.
- The exact serializer implementation, byte order, header framing, and transport reliability should be verified by tracing the called writer functions and, where authorized, comparing to network captures or server source.

**Useful follow-up:** investigate `NetEntity` component-name mapping `0x31CC80`, the parser receiving this class of message, and the two sender paths. Avoid copying raw packet assumptions into production mods.

## B. Two registration dictionaries under `NetEntity`

- `NetEntity.RegisterNetSyncVar` **`0x2F3020`**, ordinal **19,593**, uses a dictionary at roughly `NetEntity + 0x98` keyed by component name. It creates the component's list if missing, then stores a record containing the sync-variable index, parser/type information and callback/delegate.
- `NetEntity.RegisterListenerForMethod` **`0x2F2EF0`**, ordinal **19,592**, uses a **different** dictionary at roughly `NetEntity + 0x90` keyed by component name. It creates the component's listener list if missing, constructs a typed listener record and adds it.

**Why separate tables matter:** incoming state synchronization and incoming method callbacks are not interchangeable. A mod should not assume a listener registered in one map receives values intended for the other.

The native `Monster`, `Bard`, `Runemage`, `Shaman`, `Fisher`, `DynamicEvent`, `BossChest`, `DungeonBarrier` and `PortalEventNetComponent` initializers in Batch 03 demonstrate how game types populate these two structures.

## C. `OrbusNetManager` zone loading and prefab pool behavior

| Method | RVA | Static evidence |
|---|---|---|
| `LoadLevel(string zoneFile)` | `0x30B080` | Interacts with a scene-load wrapper, player/map state and several flags on `OrbusNetManager`; this is a **zone/scene transition pathway**. |
| `PreloadForScene(string zoneFile)` | `0x30B480` | Resolves zone-related prefab-name data, splits it into entries, calls `WarmupPrefabPool` for each entry with count **1**, then schedules an iterator/coroutine with observed time value **0.25 seconds**. |
| `WarmupPrefabPool(string,int,bool)` | `0x30EBD0` | Uses prefab lookup and per-name pooled instance bookkeeping, including object creation/placement and tracking. It does **not** itself demonstrate terrain chunk streaming. |
| `UpdateEntityPositions(float frameDelta)` | `0x30E350` | Iterates the manager's entity collection at approximately `+0xA8` and invokes a **virtual per-entity update method**, passing the frame delta. This is a client-side entity-update loop, not evidence of remote interest-area expansion. |
| `NotifyServerOfLoadIn()` | `0x30B320` | In the inspected native body it **only resets/toggles local flags** (fields near `+0x2D0`, `+0x2D4`, `+0x2D8`). **No direct send appears in this particular method body** despite its suggestive name; a subsequent caller or observer may perform the actual notification. |
| `SendBinary(...)` | `0x30C330` | Checks send state and chooses between two native sender paths based on a manager state value. |
| `AndroidLoadLevel(...)` | `0x3068D0` | Small coroutine factory/entry point; detailed iterator behavior lies elsewhere. |

### Why this matters for RebornCamera

The previous Batch 03 evidence establishes: (1) registered external-camera auto-cleanup above 75 units, and (2) player-avatar LOD decisions near 30/100 units. These are **presentation or object-lifetime decisions**.

The Batch 02 evidence now clarifies a third, distinct mechanism: **prefab pooling tied to zone-load preparation**. `PreloadForScene` and `ScenePreloader.Start` prewarm GameObjects, not necessarily whole scenes or distant terrain.

**Still unresolved:** What controls which terrain/scene chunks and remote entities are created, network-synchronized or culled outside the current player's interest area? That requires following scene source/bundle loading plus entity spawn/despawn handling, not merely invoking `WarmupPrefabPool`.

## Suggested private, reproducible tests

1. **Serializer envelope test:** log component name/index, method ID, entity GUID and payload class *before* send in a permitted private server session; correlate with server logs. Do not publish private player data.
2. **Zone transition:** instrument `PreloadForScene`, `LoadLevel`, `WarmupPrefabPool` and `UpdateEntityPositions`; record invocation order and whether terrain renderers enter the scene.
3. **Remote visual vs world streaming:** move only the camera (no player movement), and compare avatar LOD, spawned NPCs, terrain meshes and scene/zone state.
4. **State-registration interpretation:** monitor one of each `RegisterNetSyncVar` and `RegisterListenerForMethod` callbacks, verifying that the same numeric ID has different meanings across components.

**Evidence limit:** method names were assigned from the matching IL2CPP dump; exact semantics are supported only where branch operations were inspected. None of these native send paths prove authorization to invoke an admin action on another server.

See [Batch 03 component contracts](batch-03-server-and-network-contracts.md), [camera/world guide](batch-03-player-camera-and-world.md), and [the eight-batch research standard](batch-research-standard.md).
