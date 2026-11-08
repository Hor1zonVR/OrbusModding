# Ghidra behavior map — 2026-11-08

Practical, curated OrbusVR IL2CPP reverse-engineering findings for modders and AI coding assistants. This document records **what the code appears to do**, rather than only listing type signatures. It is not an endorsed, stable, or server-authoritative API.

## Evidence and compatibility

- **Snapshot:** `dump(2).cs`; SHA-256 `a20ae0b773fa2c37a736432e3227fb8f7fe934699879006e9c9f5873b75d54b0`.
- **Native cross-reference:** matching Il2CppDumper symbols from `script(2).json`; see [native-crosschecks.md](native-crosschecks.md).
- **Static behavior evidence:** Ghidra decompiler output supplied and examined on 2026-11-08. The original decompilation is not redistributed.
- **Build identity:** not yet verified. Never assume these addresses apply to another community or Renewed client.
- **Addresses:** VA = RVA + `0x180000000` for the analyzed image base. Tables use RVAs for easier comparison with `dump.cs` and `script.json`.
- **Confidence:** *Metadata-verified* = symbol/offset exists in the supplied dump; *static-analysis supported* = evidenced by decompiled control flow and known helper signatures; *runtime unverified* = has not been confirmed in a running game.
- Do not send undocumented component calls to public or third-party servers. Observing a client method does not establish server acceptance or permission.

## 1. Network entity primitives

| Symbol | RVA | Static finding |
| --- | --- | --- |
| `NetEntity.RegisterNetSyncVar(string componentName, byte varIdx, string type, Action<object> callback)` | `0x2F3020` | Registers a component-scoped synced variable and associated callback. |
| `NetEntity.CallServerComponent(string componentName, byte methodId, Action<BinaryWriter> callback)` | `0x2F2910` | Used by the portal to submit a client-to-server component request. Server behavior is not present in this call site. |
| `NetEntity.RegisterListenerForMethod(string componentName, byte methodId, List<string> types, Action<ArrayList> callback)` | `0x2F2EF0` | Registers a typed incoming network method listener. |

Ghidra shows `Monster.orbusNetInit(NetEntity)` (RVA `0x5B6080`) registering **13 net sync variables (indices 1–13)** and **10 typed method listeners (IDs 1, 5–12 and 14)**. This is a client-side registration table, not proof of server support for arbitrary requests.

### Monster incoming method callbacks

| Method | RVA | Observed static behavior |
| --- | --- | --- |
| `Monster.<orbusNetInit>b__14(ArrayList)` | `0x5B7F10` | Receives a byte-marked danger-zone message. Subtype 1 instantiates the `attackTelegraph` prefab (`Monster+0x90`) using transmitted position/rotation/scale data and destroys it after a transmitted duration multiplied by a small constant; subtype 2 calls `Monster.showSphereTelegraph(center, radius, duration)`. A separate received flag can trigger Animator/SFX and updates `pendingDangerZoneIdx` (`0x108`). Exact protocol labels and units need checking. |
| `Monster.<orbusNetInit>b__15(ArrayList)` | `0x5B8740` | Receives source entity GUID (16-bit), signed integer amount, and a byte flag. Updates local combat feedback, including damage/heal number presentation via a helper (`0x6683D0`), player-related notifications, and logging a combat-related message. Branches depend on signed amount and whether the source resolves to the local player. This is **presentation and notification logic**, not proof that the client computes authoritative damage. |
| `Monster.<orbusNetInit>b__13(ArrayList)` | `0x5B7C60` | Receives a string signal, includes a death-related branch setting `isDead` at offset `0x3C`, cancels a danger zone, updates Animator, emits a message/sound. Other signals trigger Animator and named SFX; exact signal text remains unidentified. |
| `Monster.<orbusNetInit>b__16(ArrayList)` | `0x5B8EF0` | Changes cast animation/UI; accesses `castingBarChild` (`0xC0`), `castingBarProgress` (`0xA0`), `castingBarText` (`0xA8`), `castingBarBreakBar` (`0xB0`), `castingBarDuration` (`0xC8`), `castingBarActive` (`0xD0`). Uses `ProgressBarPro.SetValue(float)`. |
| `Monster.<orbusNetInit>b__17(ArrayList)` | `0x5B9260` | Calls `Monster.CancelCast()` and an Animator trigger. |
| `Monster.<orbusNetInit>b__18(ArrayList)` | `0x5B9310` | Receives a VFX name, `Vector3`, and `Quaternion`; looks up a matching name in `vfxNames`, selects corresponding object from `vfxObjs`, instantiates at the supplied transform (falls back to prefab rotation for an all-zero quaternion), and destroys the spawned object after 5 seconds. Calls `Monster.triggerSfxNamed` afterward. |

**Open questions:** the other incoming method callbacks, exact network method IDs bound to each callback, and whether any message triggers the shrink coroutine. The method indices above cannot be inferred from compiler-generated callback suffixes alone; correlate with `Monster.orbusNetInit` registrations.

## 2. Public events and portal progression

| Symbol | RVA | Static finding |
| --- | --- | --- |
| `DynamicEvent.orbusNetInit(NetEntity)` | `0x404340` | Registers sync indices 1–5. |
| `DynamicEvent.<orbusNetInit>b__31_0(object)` | `0x403E20` | Changes `isActive` at `0x90`; invokes virtual activation or deactivation handler. |
| `DynamicEvent.<orbusNetInit>b__31_1(object)` | `0x403ED0` | Updates `eventDescription` (`0x78`) and a `SuperTextMesh` display. |
| `DynamicEvent.<orbusNetInit>b__31_2(object)` | `0x403F70` | Updates `detailLabel` (`0x80`) and display. |
| `DynamicEvent.<orbusNetInit>b__31_3(object)` | `0x404010` | Invokes virtual `OnDetailInfoSynced(string)`. |
| `DynamicEvent.<orbusNetInit>b__31_4(object)` | `0x404080` | Invokes `onEventSucceeded` UnityEvent when received flag is true and `isActive` is true. |
| `PortalEventNetComponent.orbusNetInit(NetEntity)` | `0x3ABA30` | Adds sync index 6 after calling base registration. |
| `PortalEventNetComponent.<orbusNetInit>b__11_0(object)` | `0x3AB980` | Stores float `progress` at `0xAC`, calls `PlayerCharacter.Instance.eventUI.SetSliderProgress(0, progress)`. |
| `PortalEventNetComponent.OnEventActivated()` | `0x3AB720` | Activates its portal object at `0x98`. |
| `PortalEventNetComponent.OnEventDeactivated()` | `0x3AB7A0` | Deactivates its portal object. |
| `Portal.RequestTeleport()` | `0x3ABF10` | Calls `NetEntity.CallServerComponent` with method ID `1`. This is portal-specific, **not** verified as a general teleport API. |

The portal event also declares `baseProgressNeeded` (`0xA0`), `progressNeededPerAdditionalPlayer` (`0xA4`), and `spawnInWaves` (`0xA8`). These are fields, not evidence that changing them locally changes server encounter behavior.

## 3. Dungeon barriers and loot

| Symbol | RVA | Static finding |
| --- | --- | --- |
| `DungeonBarrier.orbusNetInit(NetEntity)` | `0x4026E0` | Registers sync index 1. |
| `DungeonBarrier.<orbusNetInit>b__0(object)` | `0x414EB0` | Receives bool, stores `isOn` at `0x30` and calls `GameObject.SetActive` on the referenced object. |
| `BossChest.orbusNetInit(NetEntity)` | `0x42C7B0` | Registers sync indices 1–2. |
| `BossChest.<orbusNetInit>b__17_0(object)` | `0x42C480` | Stores rarity byte and enables the appropriate chest glow for rarity 2/3/4/5 (uncommon/rare/epic/legendary). |
| `BossChest.<orbusNetInit>b__17_1(object)` | `0x42C530` | Stores serialized `contents` and converts to `InventoryItemInstance[]`. |
| `BossChest.UpdateContents()` | `0x42C630` | Uses `PlayerCharacter.UpdateInventoryContainerFromString(contents)` (RVA `0x1429DC0`) and logs content. |
| `BossChest.<ShowMenu>b__18_0(WorldMenu)` | `0x42C3D0` | Clears menu and iterates `inventory` with `LootMenu.addItemToList`. |
| `BossChest.ActionChestOpened()` | `0x42BF00` | Calls `PlayerCharacter.Instance.DoLoot(chestEntityGuid)` (RVA `0x378800`). |
| `LootMenu.addItemToList(InventoryItemInstance, Document)` | `0x87F1A0` | Builds item menu markup; includes stack/stat-dependent text formatting. |

`BossChest` fields: `inventory` `0x28`, `rarityLevel` `0x60`, `contents` `0x68`.

`ExtUI.InventoryItemInstance` exposes `baseItem` `0x10`, `stacks` `0x18`, `currentDurability` `0x1C`, `metaInfo` `0x20`, `attack` `0x30`, `defense` `0x40`, and `maxDurability` `0x5C`, among other statistics. Useful for inventory UI inspection, but **not** a server-side item-grant mechanism.

## 4. Native weapon adjustment (documented for completeness)

- `PlayerClass.ToggleAdjustWeapon()` RVA `0x39AB60` and `PlayerClass.WeaponAdjusted()` RVA `0x39ACE0` dispatch through `IPlayerClass`; the shared dispatcher resides at RVA `0x0B9210`.
- `Runemage.ToggleAdjustWeapon()` RVA `0x47B1C0`, `Archer.ToggleAdjustWeapon()` RVA `0x528D20`: create/destroy a temporary adjustment object, position it near the avatar, and attach interactive components.
- `Archer.WeaponAdjusted()` RVA `0x52C310`: copies bow `Transform.localEulerAngles` to `bowDefaultAngles` `0x230`.
- `Runemage.WeaponAdjusted()` points to the shared empty method `0x2F1730` in this snapshot; do **not** assume that it commits or saves data.
- `MagicalActual.WeaponAdjuster.SubmitAdjust()` RVA `0x4A9DA0` exists as a **metadata-verified**, not yet decompiled, save/submit candidate. Do not assert PlayerPrefs persistence here.
- `MagicalActual.RigBasedAdjustment.getPositionAdjustment(PlayerAvatar)` `0x472F80` and `getRotationAdjustment(PlayerAvatar)` `0x4732E0` are controller/rig offset helpers.

## 5. Shrinking and effects

### Monster.Shrink() — real, but local-vs-network authority unverified

- `Monster.Shrink()` RVA `0x5B4990` creates a coroutine.
- Coroutine `Monster.<Shrink>d__92.MoveNext()` RVA `0x31FF00` obtains a `PlayerAvatar` and manipulates `playerBase.transform.localScale`.
- Target scale is `Vector3(0.2, 0.2, 0.2)`; interpolation duration is `1.5f`; after an approximately `8f` wait it resets the local scale to `Vector3.one`.
- On locally controlled avatars, temporarily changes `PlayerCharacter.slidingEnabled` and restores its setting using a `PlayerPrefs.GetInt` value.
- **Not established:** which server message or caller triggers it, whether nearby players observe it, support for arbitrary scales, or authoritative collision/interaction scaling.

### Status-effect and Shrinker tool traces

- `Monster.UpdateStatusEffect(float statusId, int statusType, float remaining, float original)` RVA `0x5B5780`: manages `Dictionary<float, StatusEffect>` at `Monster+0x70`; special-cases (skips the normal path for) types `18`, `57`, `66`. This does **not** identify the gameplay meaning of type `23`.
- `Shrinker.FixedUpdate()` RVA `0x488D70`: charges the held tool and calls `PlayerTool.SendToolSignal(1)` when charged; server semantics not verified.
- `Shrinker.SignalReceived(byte)` RVA `0x488F70`: handles signals 1/2 with particle/audio feedback.
- `PlayerTool.SendToolSignal(ushort)` RVA `0x3A60B0` is a further networking research target.

## 6. Scene map

- `DynamicPlayerMap.OnSceneLoaded(Scene, LoadSceneMode)` RVA `0x4057F0`: compares current zone against four special names, may clear POIs, reads `OrbusNetManager.Instance.GetCurrentZone()`, calls `InitPoI()` and `SetCurrentZoneInfo()`.
- This describes **map refresh**, not proof of far-away terrain streaming for spectator/replay cameras.

## What to investigate next — broad reconnaissance

| Area | Entry point | RVA | Why |
| --- | --- | --- | --- |
| World/scene loading | `ScenePreloader.Start()` | `0x47F540` | Discover what the preloader actually loads; may only preload assets |
| Dungeon mechanics | `DungeonShard.UseShard()` | `0x402CC0` | Inspect shard activation flow |
| Player movement | `PlayerCharacter.teleportPlayer(...)` | `0x38F5A0` | Determine local action vs network request |
| Combat telegraphs | `Monster.showTelegraph(Vector3, Vector3, float, Quaternion)` | `0x5B6CE0` | Inspect danger-area rendering |
| Combat damage UI | feedback helper called by `b__15` | `0x6683D0` | Identify damage/healing numbers and visibility |
| Player scaling | `Monster.Shrink()` | `0x5B4990` | Find references/callers, without assuming server sync |
| Items/progression | `PlayerCharacter.DoLoot(ushort)` | `0x378800` | Identify request serialization / UI |
| World events | `DynamicEvent.OnEventActivated()` | `0x403A60` | Inspect event lifecycle hooks |

## Contribution checklist

For subsequent findings, provide signature/TypeDef, snapshot/build, RVA, method behavior, corroborating callees, caller/authority context, test result, and what remains uncertain. Prefer compact explanatory writeups and safe examples over dumping third-party proprietary source code. Link to live open-source mod repositories when a feature has been implemented.
