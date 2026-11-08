# Batch 02 — Component networking, entity lifecycle and remote movement

**Analyzed source:** private Ghidra export of OrbusVR `GameAssembly.dll`, selected-function ordinals 10,001–20,000, snapshot image base `0x180000000`. Names/signatures come from the accompanying IL2CPP metadata. **Exact client build unverified.** These findings are **native static-analysis observations**, not live server/API verification.

This is a technical guide for AI assistants and multiplayer mod authors. It distinguishes a message being constructed or dispatched from a server accepting a change.

## 1. Component network messages: construction to delivery

| Operation | RVA | Observed behavior |
|---|---|---|
| `NetEntity.CallServerComponent` | `0x2F2910` | Builds a serialized outgoing message. A component-derived short ID is increased by **30,000**, followed by a **one-byte method ID**, a **16-bit entity ID** (native `NetEntity + 0x10`), and an optional payload serialized by a separate helper. It chooses one of two transport paths according to the connection manager state. |
| `NetEntity.RegisterListenerForMethod` | `0x2F2EF0` | Allocates a typed listener record and appends it to a list in a dictionary keyed by the component name, at **`NetEntity + 0x90`**. |
| `NetEntity.RegisterNetSyncVar` | `0x2F3020` | Allocates a sync-variable record containing index, type/parser information and callback, stored in a **separate** component-keyed dictionary at **`NetEntity + 0x98`**. |
| `NetEntity.TriggerListenerForMethod` | `0x2F3360` | Looks up the component method-listener group, wraps the received method ID and reader, invokes a matching typed callback via helper/delegate code, and has diagnostic/fallback paths when lookup or execution does not match expected conditions. |
| `NetEntity.UpdateNetSyncVariable` | `0x2F3C70` | Looks up the component sync-variable group, creates a typed record for incoming index and reader, invokes the corresponding callback, and has separate unknown-component/index diagnostic paths. |
| `NetEntity.ClearAllListeners` | `0x2F2AF0` | Removes one component's entries from **both** listener and sync-variable dictionaries. |

### Important restrictions

- An ID such as `1` or `12` is meaningful **only together with the component and the entity**. It is not a global admin opcode.
- The observed `+30,000` offset appears in **client message assembly**; do not assume it is the complete on-wire protocol or can be used by a server admin tool without matching handlers.
- The dispatch methods contain fallback paths for unregistered names, indexes, or mismatched callbacks; observing these can diagnose silent mod failures.
- A delegate registered in the sync-variable dictionary does not receive events registered in the method-listener dictionary.
- The exact writer functions are invoked indirectly through virtual tables, so wire byte order, length framing and transport reliability require further trace/runtime confirmation.

### Example: follow a shard tool use across two batches

`DungeonShard.UseShard` `0x402CC0` (Batch 03) → `PlayerTool.SendToolSignal` `0x3A60B0` → `PlayerCharacter.SendSignalToTool` `0x382280` → `NetEntity.CallServerComponent` `0x2F2910` (Batch 02).

The player component request at the last stage uses local method **28** with a one-byte tool selector and 16-bit signal ID. This does **not** identify the authoritative shard-consumption server handler.

## 2. Entity despawn isn't a single universal Destroy call

| Method | RVA | Native behavior |
|---|---|---|
| `NetEntity.DespawnPooled` | `0x2F2BB0` | Checks the backing GameObject, forwards entity/object cleanup to **`OrbusNetManager.ReturnToPool(GameObject,string)` `0x30BF70`** with the GameObject and prefab identifier, then clears `NetEntity + 0x18` (game object reference). |
| `NetEntity.Despawn(bool)` | `0x2F2C70` | Handles multiple cases: object already gone, active object with manager data, and immediate/delayed cleanup. A branch passes **3.0 s** for one mode or **0.1 s** for the other, then clears both listener dictionaries; it may schedule cleanup rather than deleting immediately. |
| `NetEntity.ResetPosition` | `0x2F3280` | Restores a backing Transform's position and rotation using cached position/quaternion fields (e.g. vectors near `+0x38` and quaternion near `+0x6C`). |

**RebornCamera implication:** disappearing network objects may be pooled, scheduled for delayed cleanup, or disassociated from a network entity before Unity actually destroys their hierarchy. An offline recorder must log entity identity, prefab/material/mesh dependencies, despawn/return-to-pool and last valid transform instead of assuming a missing object is a permanent game-world deletion.

**Caveat:** the 3.0/0.1 second choices are native branch constants; exactly which callers exercise each branch, and how scheduled callbacks behave across scene unloads, remains to be reproduced.

## 3. Remote motion: raw update and per-frame presentation are separate

| Method | RVA | Evidence |
|---|---|---|
| `NetEntity.UpdatePositionFromRemote(...)` | `0x2F4540` | The body reads cached positions/rotations, a configured smoothing factor based on player settings, and sets interpolation state/flags. Matching the exact seven-argument managed signature to the compiler-optimized native parameter display needs verification. |
| `NetEntity.UpdateObjectPosition(float frameDelta)` | `0x2F41D0` | Checks active interpolation flags/timer, interpolates position and quaternion values, applies a Transform and advances accumulated time. |
| `OrbusNetManager.UpdateEntityPositions(float)` | `0x30E350` | Increments a manager timer at `+0xC0`, loops a live entity collection at `+0xA8`, and invokes each entity's **virtual** position-update method with frame delta. |

### A particularly useful cross-batch discovery

`OtherPlayerEntity.OtherPlayerEntityUpdateFromRemote(BinaryReader)` **`0x32F7D0`** (Batch 03) reads several remote Transform groups and stores their interpolation targets. `OtherPlayerEntity.UpdateObjectPosition(float)` **`0x32FDA0`** renders more than the root entity: it interpolates the remote player's body and additional child transforms, including positions/quaternions for head/controller-related anchors. This is **not** safely represented by one `(x,y,z)` for the whole player.

**For synchronized replay:** capture stable network entity IDs, root body transform, head and hands/controller anchors, sample time and update/source markers, all in the same world-coordinate reference frame. During playback, separate *raw remote samples* from *interpolated displayed poses*. Do not treat interpolated frames as new authoritative server positions.

### Missing knowledge

- Exact mapping from packet types to `OtherPlayerEntityUpdateFromRemote`.
- How the server chooses which entity records to send to a client (interest management).
- How prefab pooling and scene transitions affect entity IDs.
- Whether remote player's LOD and rendering are controlled by separate world/camera distances (see [Batch 03 camera/LOD guide](batch-03-player-camera-and-world.md)).

## 4. Mod integration pattern (read-only first)

1. Trace one legitimate network entity's lifecycle on a private test server: registered → sync received → rendered → despawned.
2. Correlate `NetEntity` ID, component name, received method/index, and frame timestamp; avoid logging real usernames or sensitive payloads in public reports.
3. Match a sync callback to the real client visual change; separately verify persistence/authority on server.
4. Capture a test remote player moving arms/head while stationary; test whether a replay containing *only* root transform fails.
5. Repeat after zone change to see whether the same object is pooled or replaced.

**Confidence:** static traced for the explicit dictionaries, construction steps, transform updates and cleanup branches. Protocol framing, permission model and remote-interest radius **unresolved**. Source is not a documented or supported SDK.
