# IL2CPP symbol snapshot — curated index

These tables were automatically derived from a user-supplied IL2CPP dump for a particular OrbusVR client snapshot. The exact build identity has **not** yet been verified. These are *metadata observations*, not confirmed hook points or proof of runtime behavior.

- Source: `dump(2).cs`, SHA-256 `a20ae0b773fa2c37a736432e3227fb8f7fe934699879006e9c9f5873b75d54b0` (not redistributed).
- `script(2).json` offers native method signatures and RVA cross-references, but addresses are build-specific.
- TypeDef indices are identifiers from this dump only. Counts include compiler-generated nested types in the namespace index.
- The [namespace index](../references/magicalactual-types.tsv) lists every matched `MagicalActual` type and metadata counts.
- The [curated symbol reference](../references/core-symbols.json) includes selected field declarations and methods for high-value classes.
- Curated JSON contains **selected** fields/methods, not every member; `field_count` and `method_count` denote all parsed members in the source.

## Index highlights

| Type | TypeDef | Fields | Methods | Why inspect it |
|---|---:|---:|---:|---|
| `PlayerCharacter` | 9656 | 199 | 272 | Local player state, controllers, world/scene behavior |
| `PlayerAvatar` | 9643 | 239 | 262 | Avatar equipment, appearance, remote visuals |
| `OrbusNetManager` | 10018 | 156 | 125 | Connection management and client-side entity dispatch |
| `NetEntity` | 10029 | 22 | 14 | Networking registration, listeners, sync and component calls |
| `Bard` | 9513 | 106 | 48 | Bard class behaviors, weapons and orb handling |
| `Runemage` | 9750 | 62 | 62 | Runemage gesture input and casting-related members |
| `Paladin` | 9621 | 109 | 50 | Paladin class and weapon handling |
| `Monster` | 9862 | 51 | 40 | Enemy and player-monster state |
| `PlayerMount` | 10059 | 17 | 7 | Mount summon animation and player linkage |
| `OrbusHealthBar` | 10013 | 43 | 48 | Health/name display |
| `Potion` | 10184 | 8 | 7 | Potion object behavior |
| `Teleporter` | 9796 | 31 | 28 | Teleport mechanics |
| `InventoryManager` | 9843 | 5 | 5 | Inventory UI manager |

## Evidence & limitations

Method declarations in a dump do not contain method bodies. A method name or native RVA does not prove its semantics, call order, multiplayer authority, safety, or whether it can be patched with the configured BepInEx runtime. Confirm behaviors in Ghidra and a controlled runtime before recommending hooks. Do not assume full IL2CPP metadata is available or stable on every community client.

The index focuses on the `MagicalActual` namespace; game-relevant types also occur in the global namespace, `ExtUI`, and other assemblies, so this is not a complete game API inventory.
