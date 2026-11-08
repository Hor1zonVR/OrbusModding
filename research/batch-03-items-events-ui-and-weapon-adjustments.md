# Batch 03 — Inventory, dungeons, events, user interface and weapon adjustments

**Evidence:** User-supplied Ghidra decompilation of `GameAssembly.dll`, correlated with IL2CPP method declarations. The exact game build is unknown; RVAs are snapshot-specific. All findings below are **static analysis** unless explicitly called out as untested hypotheses.

This page is intended to help mod authors distinguish **presentation data** from **server-owned inventory, quest and equipment state**.

## A. Item movement and loot are server requests

### Inventory slot movement

`PlayerCharacter.InventoryMove(...)` **RVA `0x37E370`** creates a typed payload with:

- a source slot index and a destination slot index (observed 16-bit fields),
- an additional 16-bit value associated with the move/container,
- source and destination **container kinds** encoded as bytes. The method compares container-type strings with three known values to produce codes **1, 2, 3**; otherwise the code remains **0**.

It sends this via player-component method **5** to `NetEntity.CallServerComponent` **`0x2F2910`**. It does **not** create item instances or establish that the server will accept the move.

**Use for:** mapping inventory UI drag/drop requests and diagnosing why moving a given item fails. Pair with the actual server handler and subsequent inventory synchronization. Do not treat these numbers as a standalone public item-injection API.

### Loot interaction

`PlayerCharacter.DoLoot(ushort targetGuid)` **`0x378800`** packages the 16-bit target and sends player-component method **12**. The native body also constructs a local message and plays a UI sound after dispatch. Two direct caller functions in this batch are at **`0x3D10B0`** and **`0x42BF00`**; they should be mapped to their corresponding interactables before generalizing.

**Not demonstrated:** loot-table contents, equipment stat generation, reward ownership, or persistence. For an admin item giver, investigate authorized **server** item creation/storage paths rather than modifying this client request.

### Boss chest presentation

`BossChest.orbusNetInit(NetEntity)` **`0x42C7B0`** registers two replicated-variable slots (indices **1** and **2**). `BossChest.UpdateContents()` **`0x42C630`** converts a serialized contents value into item representation using a downstream parser and updates related presentation. This is not the same as granting a loot reward.

**Recommended trace:** replicate a chest contents update, inspect deserialization and GUI population, then trace the actual loot-claim server-side operation. Changes to the visible client list alone must not be treated as inventory persistence.

## B. Dungeons and objects with networked state

### Dungeon shards

`DungeonShard.UseShard()` **`0x402CC0`** calls `PlayerTool.SendToolSignal(1)` at **`0x3A60B0`**. The wrapper sends player-component method **28** via `PlayerCharacter.SendSignalToTool` **`0x382280`**. When certain grip states exist, the shard method also releases the held tool.

**What we can say:** shard usage is integrated with the ordinary held-tool signalling chain. **What we cannot say:** which server object consumes the shard, whether it modifies difficulty, or how the instance state persists. The authoritative receiver is still needed.

### Dungeon barriers, portals and dynamic events

- `DungeonBarrier.orbusNetInit()` **`0x4026E0`** registers state changes; previously inspected code uses a boolean to activate/deactivate the barrier GameObject.
- `DynamicEvent.orbusNetInit()` **`0x404340`** registers replicated event status fields (the existing behavior map observes five variables, representing status/description/detail/success).
- `PortalEventNetComponent.orbusNetInit()` **`0x3ABA30`** registers progress, with a local callback that updates slider UI.
- `Portal.RequestTeleport()` **`0x3ABF10`** creates an outgoing request (component method ID 1 in the inspected portal path), rather than being proof that teleportation was approved.

**Mod idea:** a read-only event state overlay driven by registered component callbacks. Distinguish event status replicated from the server from UI-only animations.

## C. Existing UI integration points

| Native method | RVA | Evidence and useful limitation |
|---|---|---|
| `PlayerCharacter.ShowNotification(string type, string message)` | `0x383210` | Creates a two-string notification record and appends it to a list at `PlayerCharacter + 0x270`. No proof of guaranteed screen delivery if HUD is hidden. |
| `PlayerCharacter.ShowKeyboard(...)` | `0x383060` | Entry point for the native keyboard workflow, with parameters controlling default text and options. Exact focus handling must be tested with the intended UI. |
| `PlayerJournal.UpdateFromString(string)` | `0x3A0E30` | Updates serialized journal state, checks for an empty/sentinel string, conditionally calls `UpdatePages()`, and clears one local state flag. |
| `PlayerJournal.UpdatePages()` | `0x3A0EA0` | Rebuild/refresh method for journal page elements; examine with live mission and quest-update events. |
| `DynamicPlayerMap.OnSceneLoaded()` | `0x4057F0` | Client map refresh on a loaded scene; does not prove terrain mesh streaming. |

**For native Mods-menu authors:** prefer an existing stable, tested menu integration in a public open-source mod over modifying global UI lists by address. These `PlayerCharacter` entry points are leads; they are not guaranteed BepInEx APIs across all Orbus builds.

**Quest tracker caution:** observing `PlayerJournal.UpdateFromString` only shows that string updates can refresh *journal pages*. It does not establish why the HUD quest tracker lags on silver-tier completion. Trace the tracker-specific binding and incoming mission updates before implementing an auto-refresh patch.

## D. Native weapon-adjustment system — a new high-priority research lead

The matching IL2CPP dump identifies a concrete class:

`MagicalActual.WeaponAdjuster : MonoBehaviour` with fields:

| Field | Snapshot field offset |
|---|---:|
| `PhysicsInteractable pi` | `0x18` |
| `ToolController toolController` | `0x20` |
| `float timeUntilDeath` | `0x28` |
| `bool isGripped` | `0x2C` |

Important methods:

| Method | RVA |
|---|---|
| `WeaponAdjuster.Start()` | `0x4A9AC0` |
| `WeaponAdjuster.SubmitAdjust()` | **`0x4A9DA0`** |
| `WeaponAdjuster.Update()` | `0x4AB6B0` |
| `WeaponAdjuster.WeaponGripped()` | `0x4AB750` |
| `WeaponAdjuster.WeaponUngripped()` | `0x4AB760` |

`SubmitAdjust()` is one of the largest relevant methods in this batch (roughly **51.8 kB of Ghidra pseudocode**). Initial native inspection shows it obtains the player and avatar's current tool/hand context, checks the active grip state and interacts with multiple weapon-related transforms and adjustment setters. Many repeated bounds checks are compiler-generated IL2CPP boilerplate; source size alone is not proof of a rich save system.

**What is NOT established yet:** the persistent save format, where the game stores weapon presets, whether adjustment data is class-specific or hand-specific, and whether this method sends a network request or only updates a client-side calibration object. These are exactly the unanswered points to test for third-party weapon-adjustment preset mods.

### Research plan for weapon adjustments

1. Trace calls to `SubmitAdjust` from `Start`, `Update`, grip/ungrip and confirmation UI.
2. Identify the actual Transform whose local position and quaternion are sampled, along with the receiver setter for those values.
3. Locate any `PlayerPrefs`, JSON, serialized settings object, config-save, or network send **downstream**; do not infer persistence from the method name.
4. Record a known unique adjustment value in a private test instance, restart, and compare before/after storage and scene fields.
5. Publish actual field mapping only after confirming which hand, class and weapon each value applies to.

The existing [WeaponAdjustments mod repository](../references/open-source-mods.md) is a practical comparison target, but its implementation and current build must be checked independently.

## E. Evidence and confidence

- **Static support:** method identities and RVAs, explicit send/registration operations, and local state/UI transformations described above.
- **Unknown:** persistence, server permissions, quest rewards, loot generation and true save semantics.
- **Testing requirement:** private/authorized Orbus instance, exact client build, reproducible inputs and observed inventory or game-state results.
- **Public data:** publish own explanations and small metadata tables, never an unreviewed bulk decompilation.
