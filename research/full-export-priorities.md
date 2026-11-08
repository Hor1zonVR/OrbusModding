# Full GameAssembly export — research priority map

**Scan date:** 2026-11-08. This is an **address/index-based prioritization**, *not* a manual review of every function's behavior.

## Provenance

- User's Ghidra decompiler export: 79,754 selected non-external functions across 400 text batch files, with 9 reported decompilation failures. Image base `0x180000000`.
- An independently built scan parsed function ordinal, VA, and RVA from all 400 files, split into 10,000-function ranges.
- We cross-referenced RVAs against the repository's [585 curated method mappings](../references/core-symbols.json). **This selected mapping covers only 48 important types.** It is not a complete list of game methods, so **zero matches does not mean zero modding value**.
- Game build identity remains unverified. No proprietary decompiler output is uploaded to this repository.

## Priority matrix

| Batch | Function ordinals | RVA span | Curated method matches (out of 585) | Decompilation failures | Priority / rationale |
|---|---|---|---:|---:|---|
| 1 | 1–10,000 | `0x1000`–`0x13FB60` | 0 | 0 | Low initially; native/IL2CPP setup and dependencies |
| 2 | 10,001–20,000 | `0x13FB70`–`0x3233F0` | **120** | 1 | High; `OrbusNetManager`, `NetEntity`, `Npc`, `OrbusHealthBar`, `Orbhealer` |
| 3 | 20,001–30,000 | `0x323450`–`0x678C80` | **465** | 4 | **Highest**; `PlayerCharacter`, `PlayerAvatar`, `Monster`, combat classes, `Fisher`, `Teleporter`, `PlayerTool`, `PlayerJournal` |
| 4 | 30,001–40,000 | `0x678CB0`–`0x979B00` | 0 | 1 | Medium; `LootMenu.addItemToList` lives at RVA `0x87F1A0`, and supporting UI code can still be relevant |
| 5 | 40,001–50,000 | `0x979C30`–`0xCBCF90` | 0 | 2 | Later, follow calls from named gameplay systems |
| 6 | 50,001–60,000 | `0xCBD010`–`0xFA2F30` | 0 | 1 | Later; includes Unity `Transform.set_localScale` at RVA `0xEBA190` |
| 7 | 60,001–70,000 | `0xFA3160`–`0x125B300` | 0 | 0 | Later, follow call graph / supporting libraries |
| 8 | 70,001–79,754 | `0x125B350`–`0x147BDB0` | 0 | 0 | Later, follow call graph / supporting libraries |

**Interpretation:** All 585 selected high-value methods in our reference fall within batches 2–3, with 465 (79.5%) in batch 3 and 120 (20.5%) in batch 2. Other namespaces and engine methods outside the curated set may be essential, so we should retain indexes of all eight batches and not discard any.

## Confirmed location examples

- Batch 2: `NetEntity.CallServerComponent` RVA `0x2F2910`, `NetEntity.RegisterNetSyncVar` RVA `0x2F3020`.
- Batch 3: `PlayerCharacter.DoLoot` RVA `0x378800`, `teleportPlayer` RVA `0x38F5A0`, `DungeonShard.UseShard` RVA `0x402CC0`, `BossChest.UpdateContents` RVA `0x42C630`, `ScenePreloader.Start` RVA `0x47F540`, `Monster.orbusNetInit` RVA `0x5B6080`.
- Batch 4: `LootMenu.addItemToList` RVA `0x87F1A0`.
- Batch 6: Unity `Transform.set_localScale` RVA `0xEBA190`.

## Suggested review order

1. Deep-research **batch 3**, focusing on player/avatar, combat, world loading, loot, and class systems.
2. Research **batch 2** for network contracts and server/client boundaries.
3. Research **batch 4** for PowerUI/loot UI and supporting presentation logic.
4. Follow the **actual caller/callee edges** to batches 1 and 5–8 as needed.
5. Publish independently written, evidence-tagged findings and reproduction steps, not raw proprietary game code.

**Important:** A Ghidra function's appearance in a batch does not make it a usable mod API. Always confirm signatures and authority with the exact game build, and validate runtime behavior in an authorized test environment.
