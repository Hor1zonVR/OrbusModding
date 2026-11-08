# Batch 04 — Rendering impostors, Oculus Avatar SDK and graph-pathfinding boundaries

**Evidence:** User's Ghidra-exported `GameAssembly.dll` functions (30,001–40,000) and corresponding IL2CPP `dump.cs` method declarations. **Snapshot base:** `0x180000000`, exact build unverified. **Confidence:** mapped / selected static-traced methods, not runtime-confirmed use of every included library.

This guide helps avoid another reverse-engineering pitfall: **an SDK or general-purpose class being inside the binary does not prove the live Orbus game actually instantiates it**.

## 1. Billboard impostors and render-texture caching

The assembly contains:

- `ImposterManager` (**TypeDefIndex 7038**),
- `ImposterProxy` (**7041**),
- `Imposter`,
- `ImposterTexture`.

`ImposterManager` has a `mainCamera`, a separate `imposterRenderingCamera`, camera-plane arrays, `imposters`, active/free `imposterTextures`, a `textureMemory` counter and a cache-mode enumeration.

| Native method | RVA | Static trace |
|---|---|---|
| `ImposterManager.LateUpdate()` | `0x7F3F40` | Periodic update over tracked/invalid impostor entries; checks manager activity and camera/culling state and schedules updates. |
| `ImposterManager.isVisible(Bounds)` | `0x7F4E20` | Forwards Bounds against stored camera planes, consistent with camera-frustum visibility testing. |
| `ImposterManager.isVisibleInCache(Bounds)` | `0x7F4DF0` | Separate visibility query against cached-camera planes. |
| `ImposterManager.getRenderTexture(ImposterProxy,int)` | `0x7F4B70` | Searches `freeImposterTextures`/cached texture lists for a matching requested resolution; assigns a proxy owner when taking a reusable entry. |
| `ImposterManager.giveBackRenderTexture(ImposterTexture)` | `0x7F4D10` | Returns a texture record to the free/reusable collection unless its backing render resource is already unavailable. |
| `ImposterManager.garbageCollect()` | `0x7F4970` | Removes unused texture/cache records and reduces the estimated `textureMemory` count. |
| `ImposterManager.Clear()` | `0x7F3AE0` | Clears tracked impostors and texture collections; the method also handles cached camera/render target cleanup. |
| `ImposterManager.ForceImposterUpdate(int)` | `0x7F3E50` | Builds a coroutine/state-machine request to update a bounded number of impostors. |
| `ImposterProxy.Init(List<Renderer>,bool)` | `0x7F5000` | Configures renderer bounds and proxy presentation, including optional shadow behavior. |
| `Imposter.Start()` | `0x7F77C0` | Initializes an impostor entry and calls renderer extraction/update helpers. |

An `ImposterProxy` exposes `quad` and `shadow` renderers and references to cached texture objects. **This represents a camera-dependent substitute rendering path**, not proof the original full-detail 3D meshes are available at every distance.

The cache policy enum distinguishes discarding invisible impostors, caching invisible impostors and preloading/caching them.

### RebornCamera implications

A replay recording a distant tree or other object **might** encounter a camera-facing quad and render texture rather than the original mesh. If the object is being rendered through this system, capturing only the proxy's transform would omit material and source-mesh information; capturing only the cached texture would not reconstruct a fly-around, six-degree-of-freedom 3D asset.

A practical capture experiment logs `ImposterManager.active`, the tracked impostor list, the proxy's mesh/quad renderers, texture allocations and current main camera. Move the player and spectator independently and observe which objects switch representation.

**Unresolved:** whether this package is active in the current Orbus build, which specific world/character objects use it, and how its thresholds relate to server entity-interest or scene loading. Do not assume all distant trees use this package.

## 2. Oculus Avatar SDK pose packets are a different system from Orbus network entities

This binary also includes `OvrAvatarPacket`, `OvrAvatarRemoteDriver`, `OvrAvatarDriver.PoseFrame`, and pose read/write helper classes.

Selected managed-method entry points:

| SDK class/method | RVA | Meaning supported by declaration/inspection |
|---|---|---|
| `OvrAvatarRemoteDriver.QueuePacket(int,OvrAvatarPacket)` | `0x6B6290` | Tracks an incoming sequence number and sends packet data to a remote-avatar SDK driver. |
| `OvrAvatarRemoteDriver.UpdateTransforms(IntPtr)` | `0x6B6860` | SDK remote avatar transform update path; precise rendering/latency behavior unverified. |
| `OvrAvatarPacket.get_Duration()` | `0x6B6160` | Accessor for packet temporal extent. |
| `OvrAvatarPacket.get_FinalFrame()` | `0x6B61C0` | Returns the final pose frame. |
| `BinaryReaderExtensions.ReadPoseFrame(BinaryReader)` | `0x77BEC0` | Reads a pose-frame representation; lengthy native body includes repeated vector/quaternion reads. |
| `BinaryWriterExtensions.Write(BinaryWriter,PoseFrame)` | `0x77C500` | Serialization counterpart for SDK pose frames. |

These are potentially useful **reference patterns for developer-designed replay serialization**, but they are **not evidence that the game uses SDK pose packets for ordinary OrbusVR party state**.

The actual game-specific remote-player path identified in Batches 2/3 is:

`OrbusNetManager.handleOtherPlayerUpdate` **`0x31D7B0`**
→ `OtherPlayerEntity.OtherPlayerEntityUpdateFromRemote` **`0x32F7D0`**
→ `OtherPlayerEntity.UpdateObjectPosition` **`0x32FDA0`**.

**Keep these pipelines separate.** A modder should verify an actual call edge from the game to any `OvrAvatarRemoteDriver` method before reusing SDK assumptions in live recording.

## 3. AstarPath and navigation libraries are also present

The snapshot contains `AstarPath`, graph/data objects and methods for:

- graph scan and updates,
- nearest-node queries,
- flood fill,
- starting/computing queued paths,
- debug graph visualization,
- scheduling graph updates.

For example, `AstarPath` exposes `ScanLoop`, `GetNearest`, `FloodFill` and `UpdateGraphs` methods in the managed dump around native RVAs `0x77....`–`0x78....`. These are a **general-purpose graph-pathfinding subsystem**; do not confuse them with `TerrainGrid`'s NavMesh/Physics-sampled cells or use them as evidence that server NPC AI follows a particular algorithm.

The more actionable game-specific navigation analysis is in [TerrainGrid and TerrainCell research](batch-04-terrain-grid-and-navigation.md).

## 4. Other notable SDK/vendor code in this range

- `OVRLipSync` and `OVRLipSyncContext`: voice/viseme tooling, with an unproven relationship to actual Orbus avatar animation.
- `P2PManager`: Oculus/platform peer-to-peer example component; no confirmed link to Orbus's ENet authoritative server traffic.
- `LocomotionTeleport`, `TeleportTargetHandlerNavMesh`, `TeleportTransitionBlink/Warp`: Oculus teleport-locomotion framework components; not automatically the `MagicalActual.Teleporter` combat/gameplay movement implementation.
- `ONSPAudioSource` / `ONSPPropagation`: spatial audio and acoustic geometry helpers; inclusion alone doesn't show which game locations use them.

## 5. Public research and testing standard

**Mapped:** the SDK classes/methods exist in the dump for this build.  
**Static-traced:** specific operations named in the first tables appear in the native decompilation.  
**Unresolved:** runtime instantiation, integration with Orbus's own classes, net authority, proprietary asset dependencies and supported mod hooks.

For a useful investigation, record a real call/scene-component reference from Orbus gameplay to an SDK object, log its lifecycle and confirm it affects the intended scene. If no caller exists, document the SDK as **bundled but unproven active**, not as a game feature.

**Modding opportunities:** renderer diagnostics, capture-fidelity metadata, visual-performance overlays and independent original replay-format inspiration. **Not proven:** a direct fix for distant terrain streaming or missing avatar meshes.
