# Ghidra Batch 03 — Orbus gameplay deep dive

**Research date:** 2026-11-08  
**Coverage:** Exported function ordinals **20,001–30,000**, RVA approximately `0x323450`–`0x678C80` of `GameAssembly.dll`.  
**Source:** User-generated Ghidra decompilation, linked to the existing [IL2CPP snapshot](il2cpp-snapshot.md) and the [curated symbol map](../references/core-symbols.json).  
**Build identity:** Unverified. Image base `0x180000000`. RVA = virtual address minus image base. Addresses are **not** portable across builds.

## Coverage and limitations

| Metric | Result |
| --- | ---: |
| Functions parsed/indexed | 10,000 |
| Successful decompilations | 9,996 |
| Failed decompilations | 4 |
| Selected, previously mapped high-value methods in this address range | 465 |
| Distinct explicit direct call relationships (excluding each function's declaration) | 61,720 |
| Direct call relationships resolved inside this same 10,000-function batch | 8,395 |
| Distinct explicit callee addresses | 4,357 |

The four failures were `0x4FFDE0` (timeout), `0x58B170` (timeout), `0x5930A0` (decompiler process failed to launch), and `0x5DFEB0` (timeout). Failure bodies are preserved in the private index for retry.

**Every behavior described below is a static-analysis finding, not a runtime-confirmed public mod API.** Native code, network permissions, dynamic dispatch, and build differences can change outcomes. All reverse-engineered pseudocode remains in the researcher's private index; only independent descriptions, names, addresses, and selective relationships are published here.

## A. RebornCamera: external-camera lifecycle and remote-player detail

### A1. Built-in external camera has a 75-unit separation check

- `MagicalActual.PlayerCharacter.FixedUpdate()`: **RVA `0x378D50`**
- `MagicalActual.PlayerCharacter.SetNewExternalCamera(GameObject)`: **RVA `0x382680`**
- `PlayerCharacter.currentExternalCamera`: field **`0x678`**

The decompiled `FixedUpdate()` checks whether `currentExternalCamera` exists, gets the camera object's `Transform.position`, reads the `PlayerCharacter` object's `Transform.position`, computes the length of their vector difference, and calls `SetNewExternalCamera(null)` when that distance is greater than **75 Unity units**.

`SetNewExternalCamera` destroys the previously stored external-camera game object (if present) and replaces the field with the new argument. Therefore the threshold is a **camera object lifecycle limit** in the built-in system, not evidence that the server stops delivering world data at 75 units.

**Why it matters:** A third-party freecam using this exact built-in external-camera registration might unexpectedly lose its camera beyond the cutoff. A camera managed independently may not be affected. Verify the call site and capture mode in RebornCamera before applying a workaround.

### A2. Remote-player LOD is not constant and is constrained by quality budgets

- `PlayerCharacter.FixedUpdate()` **`0x378D50`** directly calls `PlayerAvatar.SetToLodLevel(int)` **`0x3408C0`**.
- This branch compares player-to-avatar distances to **30** and **100** Unity units, and selects LOD indices **0–3**.
- In the observed branch, players within **30** units are candidates for LOD 0 subject to a quality-dependent near-player budget; intermediate distances/budget exhaustion can select LOD 1 or 2; beyond **100** units, or certain exclusions, the code selects LOD 3.
- The quality setting affects an internal allowance (observed values include 2, 4, 6, 8, and 10 for one budget) and priority logic. These exact values are *not* guaranteed to map one-to-one to user-visible quality labels without further research.
- `SetToLodLevel` processes distinct `lod0Renderers`, `lod1Renderers`, `lod2Renderers`, and `lod3Renderers` arrays and component changes. The method forces locally controlled avatars toward LOD 0 rather than simply applying the requested index.

**Why it matters:** Recording the existence/position of a remote avatar does not guarantee that its full-detail mesh is currently active or capturable. For replay, investigate preservation of LOD 0 rigs and geometry separately from the world/terrain problem; a forced LOD alone cannot create meshes that were never loaded or recorded.

### A3. Remote avatar smoothing and scaling reset

- `PlayerAvatar.Update()` **`0x3480E0`** conditionally interpolates `playerBase` position and rotation using `Vector3.Lerp` and quaternion interpolation, guarded by local-control/dummy-avatar checks and an update timer that is compared to **0.4 seconds**. This is a client rendering/smoothing path, not a new authoritative network update.
- `PlayerAvatar.ResetForLogout()` **`0x33FFF0`** explicitly writes `Vector3.one` to `playerBase.transform.localScale`. A mod controlling avatar size should therefore not assume its visual scale survives logout/reset.
- `Monster.Shrink()` **`0x5B4990`** creates the shrink coroutine; the coroutine's actual `MoveNext()` is outside this batch at `0x31FF00`, documented in [the broader Ghidra behavior map](ghidra-behavior-map-2026-11-08.md). Multiplayer authority remains unconfirmed.

## B. GameMaster: identified client-to-server request paths

The following methods all ultimately call `NetEntity.CallServerComponent(...)` (RVA **`0x2F2910`**, in Batch 02). The **method IDs are component-specific**. The same number in `Bard`, `Runemage`, `Shaman`, or `PlayerCharacter` does **not** mean the same server action.

| Calling type / method | RVA | Component method ID | Data / behavior observed |
| --- | ---: | ---: | --- |
| `PlayerCharacter.teleportPlayer(...)` | `0x38F5A0` | `1` | Creates destination/rotation payload, performs client-side checks and initiates teleport request; also updates local transform state. Not proof of server authorization. |
| `PlayerCharacter.InventoryMove(...)` | `0x37E370` | `5` | Packs source/destination slot indices, container GUID, and encoded inventory container types into a request. Useful for understanding item movement, not item creation. |
| `PlayerCharacter.updateServerHandState(...)` | `0x390200` | `11` | Packs hand index and state for an outgoing client message. |
| `PlayerCharacter.DoLoot(ushort)` | `0x378800` | `12` | Packs target GUID, requests loot, and plays GUI audio; actual reward delivery is server-controlled. |
| `PlayerCharacter.setHandTeleporting(...)` | `0x38E9E0` | `23` (`0x17`) | Sends a hand-identification/status payload after local checks. |
| `PlayerCharacter.SendSignalToTool(byte,ushort)` | `0x382280` | `28` (`0x1C`) | Packs one-byte tool/slot selector and two-byte signal ID. |
| `PlayerCharacter.SummonMount()` | `0x384FD0` | `60` (`0x3C`) | Sends a mount-summon request using the player entity. |
| `Bard.RegisterNoteHit(int,GameObject)` | `0x41EFC0` | `4` | Matches the struck note object to a registered instrument/note entry; sends note data after the matching conditions are met. This does not prove a numerical buff value. |
| `Runemage.finishSpellCast()` | `0x47D830` | `1` | Processes drawn gesture points against recognition data, packages qualifying gesture/stroke data, sends a cast request, then resets drawn lines. Server cast success remains distinct from attempted recognition. |
| `Shaman.SpawnTotem(byte,Vector3)` | `0x485CA0` | `1` | Packs spell/totem ID and world position for the class component. |

**Further link:** `PlayerTool.SendToolSignal(ushort)` **`0x3A60B0`** checks a locally controlled `PlayerAvatar`, converts specific tool-identifying strings to a one-byte selector, and invokes `PlayerCharacter.SendSignalToTool(...)` **`0x382280`**. `DungeonShard.UseShard()` **`0x402CC0`** is one of the callers, as is `Shrinker.FixedUpdate()` **`0x488D70`**. The matching server-side interpretation of signal IDs is **not established**.

**Important:** A client method ID is neither a free-standing administrative command nor a documented permission bypass. GameMaster should implement authorized server-side operations, not assume clients can request unrestricted changes.

## C. Combat and native game systems

| Method | RVA | Evidence-supported interpretation |
| --- | ---: | --- |
| `Monster.showTelegraph(Vector3,Vector3,float,Quaternion)` | `0x5B6CE0` | Instantiates `attackTelegraph` prefab, sets transform size, schedules destruction after duration with a small minimum. |
| `Monster.showSphereTelegraph(Vector3,float,float)` | `0x5B6B30` | Instantiates `attackTelegraphSphere` and sets its scale based on **twice** the incoming radius. Schedules timed removal. |
| `Monster.orbusNetInit(NetEntity)` | `0x5B6080` | Registers 13 sync-variable indices and multiple method listeners; previously mapped callbacks include combat/damage presentation, VFX and casting-bar state. |
| `Shaman.SpawnOrb(int,byte)` | `0x485830` | Replaces a slot's visual orb prefab, attaches it to the local Shaman object and configures the spawned effect based on spell ID; this alone is not a request for an authoritative spell effect. |
| `BossChest.UpdateContents()` | `0x42C630` | Converts a serialized contents string to inventory items using `PlayerCharacter.UpdateInventoryContainerFromString`; does not grant rewards by itself. |

### Runemage implications for CastMetrics

`finishSpellCast()` handles **recognition and an outgoing client request**. Merely invoking this method or detecting that it was entered should not be treated as a successful, server-accepted cast; a precise CPS/DPS overlay needs to distinguish attempted strokes, recognized requests, combat-log-confirmed casts, and damage dealt.

### Client-side damage feedback versus server authority

`Monster.<orbusNetInit>b__15(ArrayList)` at **`0x5B8740`** handles signed damage/healing and source GUID information for local feedback. That is valuable for diagnostics but is not evidence that the client calculates or can authoritatively set damage.

## D. User interface, journal and fishing

- `PlayerCharacter.ShowNotification(string type,string message)` — **`0x383210`**: creates a notification payload containing the two strings and adds it to a list/queue at PlayerCharacter **`0x270`**. A useful native entry point to inspect for mod notices; actual UI presentation and threading should be tested.
- `PlayerCharacter.ShowKeyboard(...)` — **`0x383060`**: existing native keyboard workflow. Use a live mod test rather than assuming the signature handles all text-field focus modes.
- `PlayerJournal.UpdateFromString(string)` — **`0x3A0E30`**: stores updated serialized journal values, checks for equality with an existing sentinel/string and calls `UpdatePages()` **`0x3A0EA0`** when appropriate. This does not establish quest tracker refresh timing.
- `Fisher.orbusNetInit(NetEntity)` — **`0x412000`**: registers a synced variable and several typed method listeners; separate `updateFishingLineOtherPlayer()` **`0x413060`** and local `updateFishingLine()` **`0x413200`** paths exist. This demonstrates a dedicated presentation path for another player's fishing line, not a generic replay/scene-capture mechanism.

## E. Scene preloading is not terrain streaming

- `ScenePreloader.Start()` — **`0x47F540`**: iterates `prefabsToConsider` and calls `OrbusNetManager.WarmupPrefabPool(prefabName,10,true)` **`0x30EBD0`**; this is prefab prewarming, **not** verified remote terrain loading.
- `DynamicPlayerMap.OnSceneLoaded` — **`0x4057F0`** updates map state/POIs, not necessarily the renderable world.

**Recommended next direction for RebornCamera:** follow `OrbusNetManager.LoadLevel` / `PreloadForScene` (Batch 02) and rendering/scene asset allocation callers before claiming support for remote world loading. Also inspect how remote LOD 0 meshes are instantiated and later released.

## Priority of outstanding questions

1. **Camera scope:** Does RebornCamera ever register its camera with `SetNewExternalCamera`? If yes, does the 75-unit auto-destroy affect it?
2. **Replay avatars:** Which code destroys/changes remote avatar LOD renderers, and how can their full-detail state be recorded before LOD degradation?
3. **World loading:** Where do scene bundles, terrain chunks, and GameObjects actually load? `ScenePreloader` is not that answer.
4. **Server request handlers:** Map the real server-side effect of each `PlayerCharacter` network method ID, rather than assuming client-only mutations persist.
5. **Combat telemetry:** Distinguish Runemage recognized strokes from confirmed casts and server-accepted damage.

## How to verify and contribute

A valid finding records a named method, RVA and build fingerprint, Ghidra control-flow evidence, runtime test steps/result and remaining unknowns. The private decompiled archive is an investigation aid; the repository publishes curated explanations instead. See [research workflow](../docs/research-workflow.md) and [Batch 01](export-batch-01-overview.md).
