# Batch 04 — Item-stat display, equipment metadata and loot UI reference

**Purpose:** Help modders build accurate item tooltips, character/inventory browsers, read-only analytics and private-server GameMaster interfaces.  
**Provenance:** matching IL2CPP `dump.cs` class declarations for `ExtUI.InventoryItemInstance` and `ExtUI.InventoryItemMeta`, plus **Batch 04** `LootMenu` presentation-method native pseudocode. **Exact game build unknown**. Some item-model methods actually fall outside Batch 04; this is a cross-batch *data reference*, not a claim they were decompiled in Batch 04.

## 1. The actual item instance fields

`ExtUI.InventoryItemInstance`, `TypeDefIndex 9191`:

| Field | Snapshot offset | UI meaning / caution |
|---|---:|---|
| `InventoryItem baseItem` | `0x10` | Item template/base definition (name, type, base appearance elsewhere). |
| `int stacks` | `0x18` | Instance count; may exceed 1 for stackable items. |
| `int currentDurability` | `0x1C` | Current durability (integer). |
| `InventoryItemMeta metaInfo` | `0x20` | Additional item metadata, below. |
| `bool isTradable` | `0x28` | Client-visible tradability flag, not necessarily full server transfer permission. |
| `int armor` | `0x2C` | Effective/instance armor value in the client model. |
| `int attack` | `0x30` | Effective/instance attack value. |
| `int strength` | `0x34` | Strength. |
| `int intellect` | `0x38` | Intellect. |
| `int regen` | `0x3C` | Regeneration. |
| `int defense` | `0x40` | Defense. |
| `int magdefense` | `0x44` | Magical defense. |
| `int vitality` | `0x48` | Vitality. |
| `int crit` | `0x4C` | Critical stat. |
| `int wisdom` | `0x50` | Wisdom. |
| `int speed` | `0x54` | Speed. |
| `int luck` | `0x58` | Luck. |
| `int maxDurability` | `0x5C` | Maximum durability. |
| `int itemLevel` | `0x60` | Item level. |
| `int itemPlusLevel` | `0x64` | Enhancement/plus level. |
| `string rarity` | `0x68` | Rarity label/identifier. |
| `bool perfect` | `0x70` | Perfect marker. |
| `string loadout` | `0x78` | Loadout metadata string. |

**Display example:** A tooltip can show item name from `baseItem`, **Level `itemLevel` · +`itemPlusLevel` · rarity · `currentDurability/maxDurability`**, then only nonzero instance stats. Use string/enum values actually returned by the client; do not invent the game's item rarity tiers or stat formula.

## 2. Rich `InventoryItemMeta` metadata

`ExtUI.InventoryItemMeta`, `TypeDefIndex 9192`:

| Field(s) | Offset(s) | Why a mod author may care |
|---|---|---|
| `parts`, `tileset`, `mutations` | `0x10`, `0x18`, `0x20` | Appearance/variation information. |
| `sharddungeon`, `shardlevel` | `0x28`, `0x30` | Shard association/difficulty metadata. |
| `majordye`, `minordye` | `0x38`, `0x40` | Cosmetic dye fields. |
| `durability` | `0x48` | Stored metadata durability; do not automatically substitute for `currentDurability` without testing. |
| `tempTradable` | `0x50` | Temporarily tradable-related strings. |
| `strength` through `luck` | `0x58`–`0x84` (with intervening stat fields) | Stored per-stat metadata; **may differ** from effective `InventoryItemInstance` values. |
| `maxDurability` | `0x88` | Stored maximum durability metadata. |
| `rarity` | `0x90` | Metadata rarity. |
| `affixes` | `0x98` | Affix descriptors (array of strings). |
| `perfect` | `0xA0` | Stored perfect flag. |
| `primaryColor`, `secondaryColor`, `spotColor` | `0xA8`, `0xB0`, `0xB8` | RGB-ish arrays; verify exact component format in the game. |
| `size`, `type` | `0xC0`, `0xC8` | Metadata size/type. |
| `mood`, `happiness`, `bonusType`, `rollLevel` | `0xD0`, `0xD4`, `0xD8`, `0xDC` | Specialized item/pet/roll fields; do not assign universal meanings. |
| `looksLike` | `0xE0` | Cosmetic/appearance override hint; decoding not established. |
| `itemLevel`, `itemPlusLevel` | `0xE4`, `0xE8` | Original metadata counterparts to instance-level fields. |
| `containedItems` | `0xF0` | String array of nested/contained items. |
| `loadout`, `locationId` | `0xF8`, `0x100` | Loadout/location metadata. |
| `expireTime`, `locked`, `breederName` | `0x108`, `0x110`, `0x118` | Expiration/lock/origin fields. |

**Do not equate** a metadata field with a mutable authoritative stat. The client may be reading values synchronized from the server and may reconstruct effective values from metadata plus base item data.

## 3. Where these values actually appear in the UI

`LootMenu.addItemToList(InventoryItemInstance,Document)` **RVA `0x87F1A0`** uses the instance's base-name, rarity (`+0x68`), stack count (`+0x18`), and positive attack (`+0x30`) / armor (`+0x2C`) branches when constructing markup for an existing document element.

`LootMenu.clearList(Document)` **`0x87F5B0`** clears the list content in the document.

**Important limitation:** these display functions do **not** automatically expose every potential item stat. A custom stats panel can display more fields than the stock loot-list entry, but it should use the original item instance rather than trying to parse the generated HTML back into structured data.

`AuctionHouseMenu.AuctionHouseItem.invItem` (**offset `0x58`**) gives auction listings access to an `InventoryItemInstance`. Other fields include `bid` (`0x40`), `buyout` (`0x44`) and `stackSize` (`0x38`). Avoid confusing a listing's advertised quantity with the underlying item's own stack count.

## 4. Practical implementation guidance

### For an inventory browser / GameMaster dashboard

- Map each inventory slot to **stable item identity, baseItem identifier and instance metadata** where accessible.
- Render `itemLevel`, `itemPlusLevel`, rarity, effective stats and current/max durability separately.
- Use locally available sprite/icon references **only after identifying how the base item resolves to an icon**; the existence of `baseItem` does not by itself reveal a sprite atlas key. This remains unresolved and is a good next reverse-engineering target.
- Display zero/empty/missing stats truthfully; don't fabricate stats for test-admin items that arrive with unset metadata.
- If editing inventory on a private server, go through **authorized server-side data structures and persistence**, then verify that the client receives the expected recomputed values. Writing the client object alone does not create a persistent or legitimately equipped item.

### For item tooltip mods

- Try ordinary item, +enhanced item, broken item, equipped appearance/transmog and tradable/non-tradable instances.
- Check whether `InventoryItemInstance.maxDurability` and `metaInfo.maxDurability` agree.
- Confirm whether rarity string is a display name or machine token by observing the native UI and stored item values.
- Test whether `looksLike`, dyes and `primaryColor` affect rendering; don't infer the exact shader algorithm from field names.
- Avoid saving other players' private inventory contents unless the game/server explicitly permits it.

## 5. Cross-batch method references

The item instance's managed methods in the matching metadata reside at RVAs **`0x14315F0`** (constructor from serialized item string), **`0x1431A90`** (`isBroken()`), **`0x142EDD0`** (`GetAppearanceId()`) and **`0x142EE00`** (`MetaDescription()`). Those RVAs are **outside Batch 04** and their full native behavior has **not** been re-examined for this page.

That makes this a useful follow-up for **Batch 8**, where core item parsing/appearance behavior is more likely to be found.

**Evidence labels:** field names and offsets = **dump-mapped**; LootMenu branching and DOM construction = **static-traced**; stat formulas/icon resolution/server edit permissions = **unresolved**. Always verify on the exact client build.
