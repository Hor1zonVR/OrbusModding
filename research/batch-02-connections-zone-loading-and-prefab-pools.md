# Batch 02 — Connections, scene transitions, player initialization and prefab pools

**Data source:** native Ghidra export, ordinals 10,001–20,000, metadata names from matching IL2CPP dump. **Image base:** `0x180000000`. **Build identification:** not confirmed; **all findings are static analysis**. This guide provides a workflow for networking, level-loading, freecam and multiplayer mod authors without redistributing the decompiled binary.

## 1. Initial connection versus later gameplay traffic

| Named method | RVA | Behavior evidenced by native body |
|---|---|---|
| `OrbusNetManager.EnetClient()` | `0x308C10` | Runs a native network service loop while a manager flag is set; recognizes multiple connection/disconnection/receive event types, converts incoming bytes and enqueues received messages for later processing. |
| `OrbusNetManager.EnetSender()` | `0x3091B0` | Runs a separate loop while an outgoing-sender flag is set; drains a send queue, creates native transport packet structures, and submits them for sending. |
| `OrbusNetManager.sendConnectionAttempt()` | `0x31F720` | Constructs a connection-attempt text/message through `Send(string)` **`0x30CF90`**. |
| `OrbusNetManager.sendToken()` | `0x31F9A0` | Constructs a message from current connection and authentication-related fields and sends it via `Send(string)`. **Never log or commit actual token values.** |
| `OrbusNetManager.sendPing()` | `0x31F790` | Uses a binary writer with observed leading integer **`0x28` (40)**, writes a timestamp calculated from engine time × 1000 and rounded, then writes byte **`0x41`**, dispatching through state-dependent transport. |
| `OrbusNetManager.SendInitialPosition(Vector3)` | `0x30C3B0` | Writes an initial-position message beginning with integer **10**, followed by three 32-bit floating-point position components. Uses either queued/native transport path according to connection state. |
| `OrbusNetManager.SendBinary(...)` | `0x30C330` | Checks a send/connection flag and dispatches to one of two native transport paths, rather than unconditionally transmitting. |

**Why this matters:** a function labelled “send” can be invoked before the network is actually ready or during a failed/transitioning connection. A gameplay mod should distinguish **queued attempt**, **transport delivery**, **server acknowledgement**, and **replicated result**.

**Wire-format caution:** these leading constants and writes are visible in the *native writer operations* of this specific build. They are not sufficient to implement a robust standalone protocol client. Writer byte order, length framing, encryption/compression if any, and server validation remain to be established.

## 2. The native network client has two distinct execution loops

`EnetClient` processes native connection events. In the inspected loop:

- A connection-type event changes state and triggers `sendToken()`.
- A disconnection-type event routes to an error/display branch.
- A receive-type event extracts native packet bytes, constructs managed byte/text representations, and dispatches them to managed queues/handlers.
- A periodic counter can trigger a connection-attempt send while not yet connected.

`EnetSender` does **not** parse game messages. It reads the pending send queue, serializes native transport packet objects, and submits them while its running flag remains set. This matters for crash diagnostics: client-side message construction and later physical transport are distinct points of failure.

**Unresolved:** exact OS/thread ownership, whether all gameplay sends use this queue, and how the receive parser maps every numeric message type into `NetEntity` handlers. Do not call these methods directly from a BepInEx plugin without verifying threading.

## 3. Scene transitions: a zone load does multiple things

`OrbusNetManager.LoadLevel(string zoneFile)` **`0x30B080`**:

1. Builds/logs a zone-related message.
2. Calls a Unity scene-loading function with the provided zone file (native helper `0x180EACB20`), under other transition/setup calls.
3. Resets related display/player/map objects when present.
4. Calls **`OrbusNetManager.activatePrimaryScene(string)` `0x31C6F0`** with the zone name.
5. Updates several manager flags near `+0x2D0`, `+0x2D4`, `+0x2D8` and `+0x2A8`.

It is a **whole zone/scene transition path**. It is *not* evidence that a spectator camera can freely load arbitrary terrain independently of the local player's zone.

### Important naming trap: `NotifyServerOfLoadIn()` does not send here

In the actual body of `OrbusNetManager.NotifyServerOfLoadIn()` **`0x30B320`**, the only visible operations are to reset a manager integer at `+0x2D4` and conditionally toggle flags `+0x2D0` and `+0x2D8`. **No direct network send appears in that function body.**

That means “call NotifyServerOfLoadIn to send a server packet” is **not demonstrated**. A different update loop may observe its flags and later send something. Trace its callers and downstream flag readers first.

## 4. Prefab preloading, object pools and their boundaries

`OrbusNetManager.PreloadForScene(string zoneFile)` **`0x30B480`** gets zone-related prefab names, splits their list, calls `WarmupPrefabPool(prefabName, 1, true)` for each item, then schedules a coroutine with initial delay **0.25 s**.

`OrbusNetManager.WarmupPrefabPool(string prefabName, int count, bool ...)` **`0x30EBD0`**:

- Calls a separate prefab lookup/registration helper.
- Looks up a dictionary of prefabs at manager offset `+0x288` and pooled instance lists at `+0x290`.
- Ensures the cached number of instances meets the requested count.
- Creates instances in a **far-off holding position**, with vector values from `0xC61C3C00` (a large negative coordinate), and adds them to the pool.
- Optionally records the prefab key in another collection at `+0x2A0` so the manager can track warmup completion/state.

Note that this is **managed prefab instance caching**, *not* streaming distant terrain. Scene mesh availability, terrain chunk boundaries, collider creation and server-controlled entity spawning remain distinct questions.

A separate `ScenePreloader.Start()` at **`0x47F540`** (Batch 03) warms each configured prefab at count **10**, illustrating that warmup count depends on the caller.

The same snapshot also has **`OrbusNetManager.GetPrefabFromPool(string)` `0x309BF0`** and **`ReturnToPool(GameObject,string)` `0x30BF70`**. The latter is invoked by `NetEntity.DespawnPooled()` **`0x2F2BB0`**, completing a direct object-pool lifecycle link from entity cleanup to the manager's prefab caches.

## 5. Player rig initialization and switching

`OrbusNetManager.initializePlayerRig(ushort playerId, Vector3 position, Quaternion rotation)` **`0x31EF50`**:

- If there is no current player-rig object at manager offset `+0x60`, constructs the rig and adds it to the manager's entity collection **`+0xA8`** and ID lookup **`+0x388`**.
- If a rig already exists, it removes a previous ID mapping, iterates entities for a matching player ID and may despawn a previous representation, then reassigns the rig's player ID/lookup mapping.
- Its exact lifecycle branch depends on current manager state and entity active flags. It does not mean two remote players can freely share one authoritative ID.

**Why this matters for replay:** when entering/leaving instances, entity IDs and GameObject identities can be rebound. Use a session-scoped identity and **record a clear zone/scene boundary**; do not blindly merge entities based only on a transient short network ID.

## 6. RebornCamera investigation map

| Camera/replay question | Start with | What must be tested |
|---|---|---|
| Why is remote terrain absent? | `LoadLevel` `0x30B080`, Unity scene loader, zone/asset dependencies | Does the scene loader provide static terrain meshes after the camera alone moves? |
| Why are far-off NPCs missing? | `WarmupPrefabPool` `0x30EBD0`, spawn/despawn, server interest filtering | Is a prefab missing, an entity unspawned, or an object returned to pool? |
| Why do player models downgrade? | `PlayerCharacter.FixedUpdate` `0x378D50`, `PlayerAvatar.SetToLodLevel` `0x3408C0` | Is the desired rig/mesh already available when LOD drops? |
| Why do remote poses look stiff? | `UpdateEntityPositions` `0x30E350`, `OtherPlayerEntityUpdateFromRemote` `0x32F7D0` | Are head/hand transforms missing or just not being replayed? |
| Why does a built-in camera disappear? | `SetNewExternalCamera` `0x382680` and its 75-unit check | Is the mod's camera registered through that game-owned reference? |

## Safe reproduction procedure

Use an authorized local/private test server, record only test accounts, and instrument **read-only** timing plus scene identifiers for these methods. Compare (a) camera-only movement, (b) actual player zone movement, and (c) spectator playback with cached assets. Do not force the authoritative player coordinate just to trick remote loading without validating persistence and game-state consequences.

**Status:** well-supported client-side networking and scene/pooling code paths. **Not solved:** arbitrary remote terrain streaming, authoritative interest-area selection, and complete live server packet schema.
