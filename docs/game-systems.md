# Game systems — first IL2CPP investigation map

This is a curated **metadata** map from the uploaded OrbusVR IL2CPP snapshot. It does not claim that these methods are safe mod hooks. Names, access modifiers, signatures and RVAs below are taken from the dump; exact behavior and authority require Ghidra inspection/runtime tests.

**Snapshot:** `dump(2).cs`, SHA-256 `a20ae0b773fa2c37a736432e3227fb8f7fe934699879006e9c9f5873b75d54b0`. Game build identity not yet confirmed.

## Player, avatar and movement

- `MagicalActual.PlayerCharacter` (TypeDef 9656): 199 fields, 272 methods. Local controllers, scene/menu references, the avatar, movement-related declarations.
  - `public void SummonMount()` — RVA `0x384FD0`
  - `public void Dismount()` — RVA `0x378590`
  - `public void teleportPlayer(Vector3 destination, Nullable<Quaternion> rotation, bool doFade = True, bool freeTeleport = False)` — RVA `0x38F5A0`
  - `public void InventoryMove(ushort oldidx, string oldtype, ushort newidx, string newtype, ushort containerGuid)` — RVA `0x37E370`
- `MagicalActual.PlayerAvatar` (TypeDef 9643): 239 fields, 262 methods. Has `playerMountPosition`, `mountSlot`, and `equipmentBySlot` related members.
  - `private void SetMount(bool mounted)` — RVA `0x340310`
  - `public void equipGear()` — RVA `0x34B1B0`
- `MagicalActual.PlayerMount` (TypeDef 10059): contains `player`, `avatar`, `MountSummoned` fields and mount animation methods.
- `MagicalActual.PlayerRig` (TypeDef 10062): includes `eyeCamera` and controller hint methods.

## Classes and combat

- `MagicalActual.Bard` (TypeDef 9513): 106 fields, 48 methods.
  - `public void RegisterNoteHit(int noteIndex, GameObject thisGameobject)` — RVA `0x41EFC0`
  - `public void SuperStatusChange(bool superActive)` — RVA `0x41F6D0`
  - `private void UpdateBeltOrbs()` — RVA `0x420EC0`
- `MagicalActual.Runemage` (TypeDef 9750): 62 fields, 62 methods; gesture-related fields including `recognizerPoints` and `spellPathLines`.
  - `private void finishSpellCast()` — RVA `0x47D830`
  - `public void CastSpark()` — RVA `0x479150`
- `MagicalActual.Paladin` (TypeDef 9621): includes weapon and super-related members, such as `public void SuperStatusChange(bool superActive)` at RVA `0x334EC0`.
- `MagicalActual.Monster` (TypeDef 9862): 51 fields, 40 methods, including `hitPointsReadOnly`, `isDead`, and `public bool HasStatusEffect(int statusType)` at RVA `0x5B44B0`.
- `MagicalActual.DamageParams` (TypeDef 9484): fields `int damageAmount` and `DamageAffinity affinity`.
- `MagicalActual.StatusEffectParams` (TypeDef 9482): fields `effectName`, `effectDuration`, `effectParam1`, `effectParam2`.

## Multiplayer and scene loading

- `MagicalActual.OrbusNetManager` (TypeDef 10018): 156 fields, 125 methods.
  - `public void DoConnect()` — RVA `0x3084E0`
  - `public string GetCurrentZone()` — RVA `0x309BE0`
  - `public void SendBinary(byte[] bytes, long payloadSize, bool reliable = True, byte channelOverride = 0)` — RVA `0x30C330`
- `MagicalActual.NetEntity` (TypeDef 10029): component listener and sync declarations.
  - `public void CallServerComponent(string componentName, byte methodId, Action<BinaryWriter> callback)` — RVA `0x2F2910`
  - `public void RegisterListenerForMethod(string componentName, byte methodId, List<string> types, Action<ArrayList> callback)` — RVA `0x2F2EF0`
- `MagicalActual.OtherPlayerEntity` (TypeDef 10034) and `MagicalActual.PlayerEntity` (TypeDef 10035) are distinct types. Do not assume either has the same authority as the server.
- `MagicalActual.ScenePreloader`, `MagicalActual.Portal`, `MagicalActual.DungeonShard`, and `MagicalActual.Teleporter` are additional investigation targets.

## UI and miscellaneous

- `MagicalActual.InventoryManager` (TypeDef 9843): `public void Open()` at `0x3CD0C0`; `public void Close()` at `0x3CD050`.
- `MagicalActual.OrbusHealthBar` (TypeDef 10013): health bar, naming and visibility methods.
- `MagicalActual.Potion` (TypeDef 10184) and `MagicalActual.PotionAgingStation` (TypeDef 10081) are distinct.
- `MagicalActual.Fisher`, `MagicalActual.FishingRod`, and `MagicalActual.FishingLure` are possible fishing investigation entry points.

## How to follow up

1. Search the full [namespace type index](../references/magicalactual-types.tsv).
2. Open [curated machine-readable symbols](../references/core-symbols.json).
3. Identify the precise method signature and RVA.
4. Compare with `script.json` and investigate the matching code in Ghidra.
5. Reproduce the behavior on the intended client build before writing or endorsing a hook.
6. Inspect [public reference mods](../references/open-source-mods.md) for working implementation patterns.

**Caution:** Method metadata is not the same as a stable public API. Use authorized test environments and do not assume client-sent networking methods bypass server authority.
