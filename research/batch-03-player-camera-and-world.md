# Batch 03 — Player, camera, avatars and world-loading boundaries

**Snapshot:** Community/OrbusVR IL2CPP `GameAssembly.dll` export, image base `0x180000000`, exact build unknown. **Evidence:** inspected Ghidra decompilation plus method names from the matching `dump.cs` snapshot. **Status:** static analysis, **not runtime-confirmed**. RVA addresses must be rechecked against the user's game build.

This guide is designed for anyone building spectator cameras, avatar scale/appearance mods, video replay capture, or world/scene debugging. See [Batch 03 overview](export-batch-03-deep-dive.md) and [research standards](batch-research-standard.md).

## 1. External-camera lifetime: five visible callers and a distance cap

Native-method chain:

| Method / finding | RVA | Evidence |
|---|---|---|
| `PlayerCharacter.FixedUpdate()` | `0x378D50` | Reads `currentExternalCamera` field at `PlayerCharacter + 0x678`, gets its transform position, calculates distance to player's position; if **greater than 75 units**, invokes `SetNewExternalCamera(null)`. |
| `PlayerCharacter.SetNewExternalCamera(GameObject)` | `0x382680` | Destroys the *previously registered* camera GameObject when present, then replaces the stored reference. |
| Other direct callers | `0x378AB0`, `0x385F70`, `0x42E530`, `0x42E7F0` | Four other code sites invoke the same camera setter; their high-level caller identities/lifecycles need mapping before assuming the camera is exclusively controlled by FixedUpdate. |

There are **five** direct same-batch caller functions in total, counting `FixedUpdate`. The 75-unit condition is a client-side **lifecycle rule for a registered external camera object**. It does *not* imply a 75-unit world-rendering, scene-loading or network-interest radius. Camera objects managed completely independently might not enter this path.

**Mod integration checklist:** Determine whether your camera is registered with this setter. In a disposable/private test instance, log registration, camera GameObject destruction, player-camera distance and scene changes. Test distances below and above 75 units, both while mounted and after re-entering a zone. Never disable a distance guard blindly; other code may depend on its cleanup behavior.

## 2. Remote avatar LOD selection and capture fidelity

Native-method chain:

- `PlayerCharacter.FixedUpdate()` `0x378D50` directly calls `PlayerAvatar.SetToLodLevel(int)` `0x3408C0`.
- `PlayerAvatar.SetToLodLevel` also has direct same-batch caller sites at `0x343970` and `0x345790`; those callers may represent separate state changes.
- The distance-selection branch uses **30** and **100** Unity-unit thresholds and integer LOD levels **0, 1, 2, 3**.
- Near players (up to 30 units) may qualify for highest detail but are subject to per-quality budgets; when a budget fills, lower LODs may be chosen even at relatively short distances. Distant players (past 100 units) can be assigned level 3.
- The avatar method manipulates distinct renderer collections (`lod0Renderers`, `lod1Renderers`, `lod2Renderers`, `lod3Renderers`) and treats locally controlled avatars specially.

**Important:** LOD 3 does not automatically mean despawned. LOD loss is different from never receiving an entity, not loading mesh/prefab assets, or destroying a GameObject. The camera recorder must distinguish all four cases.

**For a replay mod:** record an entity's stable identity, world-space transform, scene/zone identity, prefab or mesh identification, available skin/equipment material state, active LOD and actual scene object availability. Test what happens when a remote player crosses 30 and 100 units. If only low-detail meshes were ever present, changing the current LOD property after recording will not synthesize missing geometry.

## 3. Remote-player smoothing is a separate visual layer

`PlayerAvatar.Update()` at **`0x3480E0`**:

- Exits early for locally controlled avatars, dummy avatars or other gating flags.
- In the observed path uses an update timer that stops when it reaches **0.4 s**.
- Interpolates a player-base Transform's position/rotation between stored values. This is **client-side presentation**, not proof of the frequency or exact wire format of network snapshots.

**Mod test:** log raw remote entity position updates (once identified in Batch 02) alongside the rendered avatar's Transform each frame. Distinguish jitter induced by network timing from smoothing loss in offline replay.

## 4. Avatar scale resets across lifecycle events

`PlayerAvatar.ResetForLogout()` **`0x33FFF0`** constructs `Vector3(1,1,1)` and sets `playerBase.transform.localScale` to that value. Its visible direct caller in this batch is at `0x385440`. Therefore a visual scale modification may not survive logout or pooling/reset. `Monster.Shrink()` **`0x5B4990`** is another game-owned scale-changing pathway; its animation coroutine lies in Batch 02 (`0x31FF00`).

**Do not conclude:** changing this client-side scale updates hitboxes, combat reach, server authority, or other players' views. Those require separate verification.

## 5. Prefab warmup is not remote terrain streaming

`ScenePreloader.Start()` **`0x47F540`** iterates `prefabsToConsider` and calls `OrbusNetManager.WarmupPrefabPool(prefabName, 10, true)` at **`0x30EBD0`**. This strongly supports **prefab-pool prewarming**. It is not evidence that remote terrain/chunks load or that a spectator receives entities outside the player-based interest area.

`DynamicPlayerMap.OnSceneLoaded` **`0x4057F0`** concerns player-map state; a visible map does not prove the underlying terrain mesh is loaded.

**Next evidence required:** trace `OrbusNetManager.LoadLevel` **`0x30B080`**, `PreloadForScene` **`0x30B480`**, level/asset-bundle creation, entity spawn/retirement, and remote-interest updates (primarily Batch 02). Test world objects separately from NPC rigs and avatar rigs. Do not artificially move the real player's authoritative position without considering server-side game rules or player safety.

## Modder-oriented experiments

1. **Camera lifetime:** register a native external camera in a private game session and observe exactly when the GameObject is destroyed; compare with independently managed freecam.
2. **Avatar fidelity:** place two consenting test players at controlled distances and log LOD indices, active mesh renderers, and scene-object lifetime.
3. **Replay reconstruction:** persist pre-LOD-downshift appearance assets when legitimately available and verify offline playback with and without the live player present.
4. **Terrain loading:** change only the spectator camera position and measure whether scene objects, collision and terrain renderers appear; then compare with normal scene travel and zone load.

**Status:** the exact camera destruction branch, LOD threshold branches, smoothing and scale reset have been inspected in native pseudocode. Replay remediation and distant terrain acquisition remain **hypotheses** pending runtime tests.
