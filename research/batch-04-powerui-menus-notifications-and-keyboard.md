# Batch 04 — Native PowerUI menus, notifications, keyboard and loot display

**Source:** Ghidra-exported OrbusVR IL2CPP native code from function ordinals 30,001–40,000, matched to `dump.cs` UI class names. **Snapshot image base:** `0x180000000`; build fingerprint unverified. Findings describe **client-side presentation code**, not authoritative server state and not guaranteed public mod APIs.

This page is intended for UI/accessibility mod authors, including people extending RebornMenu/ModCore.

## 1. The game already uses native `Document` and `Element` objects

Several classes expose APIs taking **`Document`**, **`Element`** and **`UIEvent`** rather than creating Unity uGUI objects directly:

- `LootMenu.addItemToList(InventoryItemInstance, Document)` — RVA **`0x87F1A0`**
- `LootMenu.clearList(Document)` — **`0x87F5B0`**
- `NotificationMenu.ShowNotification(string,string,Document)` — **`0x6F9D60`**
- `KeyboardMenu.SetText(string,Document)` — **`0x7C83E0`**
- `ObjectOptionMenu.AddChoice(string,bool,Document)` — **`0x7C0150`**
- `AuctionHouseMenu.addAuctionListings(...)` — **`0x7731C0`**

The native decompilation makes frequent calls to `FUN_180a96a10` (document/element lookup), `FUN_180ba9740` (element text/HTML setter), and other string/DOM manipulation methods, while specific managed signatures are cross-referenced from `dump.cs`. **We have not independently established the exact PowerUI method name for every anonymous helper.** Verify in BepInEx interop/game build before writing a patch.

**Mod principle:** keep a stable reference to the *currently active* `Document`; a document or element created in an earlier scene/menu open is not automatically valid after closing and reopening.

## 2. Loot-menu display is a renderer, not an item-grant function

`LootMenu.addItemToList(InventoryItemInstance item, Document document)` **`0x87F1A0`**:

1. Requires a non-null item with non-null `baseItem`.
2. Builds display text using the item's base-name field and data fields.
3. Reads `InventoryItemInstance.rarity` (**`+0x68`**) to choose a rarity-related string/markup variation.
4. Adds conditional stack information if `stacks` (**`+0x18`**) is greater than 1.
5. Adds conditional displayed stats when `attack` (**`+0x30`**) or `armor` (**`+0x2C`**) is positive.
6. Looks up a list `Element` in the supplied `Document`, reads current contents, appends the constructed markup and writes the updated content back.

**`LootMenu.clearList(Document)` `0x87F5B0`** finds the same list element and sets its content to an empty string in the observed path.

**Critical distinction:** the native path does **not** create an `InventoryItemInstance`, credit a reward, or send a server request. It is only a UI renderer. To investigate the real loot transaction, trace `PlayerCharacter.DoLoot(ushort)` **`0x378800`** (Batch 03), the incoming result handler and server-side item mutation separately.

**Useful mod:** show full equipment stats in a richer loot tooltip without modifying the underlying item. This can help accessibility and give players a better preview of dropped equipment.

## 3. NotificationMenu handles timed DOM-based alerts

`NotificationMenu.ShowNotification(string type,string message,Document document)` **`0x6F9D60`**:

- Finds multiple alert-related elements in the supplied `Document`.
- Writes the message string into a text/HTML element.
- Creates a closure with an `alertbox` `Element` reference.
- Schedules two animation callbacks with constants **0.5 seconds** and **5.5 seconds** in the inspected native body.
- Chooses one of several style/markup variants based on the `type` input; exact string literals were not decoded from the `stringliteral.json` snapshot in this pass.

The closure methods `NotificationMenu.<>c__DisplayClass0_0.<ShowNotification>b__0()` **`0x716310`** and `b__1()` **`0x716370`** call separate element transition/animation helpers.

**Practical design:** for a mod notification, use the game's standard notification pathway when verified in-game, and guard against a closed/invalid `Document`. The presence of a callback schedule is not proof alerts always stay visible for 5.5 seconds in every scene.

## 4. Keyboard input is a reusable stateful native UI

`KeyboardMenu` has static fields for ordinary/shifted/alternative/numeric row layouts and the boolean flags:

- `shiftDown` at **`0xA8`**;
- `altDown` at **`0xA9`**;
- `acceptInput` at **`0xAA`**.

| Method | RVA | Static behaviour / use |
|---|---|---|
| `firstOpen(Document,bool numericOnly)` | `0x7C8DD0` | Chooses ordinary vs numeric keyboard creation based on the input flag. |
| `makeKeyboard(Document)` | `0x7C8F80` | Builds the row markup from current/shifted/alternate layout strings. |
| `makeNumericKeyboard(Document)` | `0x7C93D0` | Builds separate numeric layout rows. |
| `clickKey(UIEvent)` | `0x7C8810` | Handles keyboard key input; modifies a static input string, includes delete/backspace-like branch and an enter/submit branch. |
| `SetText(string,Document)` | `0x7C83E0` | Updates the current string and a matching `Document` element. |
| `enterPressed()` | `0x7C8D00` | Invokes a separate input/submit helper, then resets text and both modifier flags. |
| `toggleShift(UIEvent)` / `toggleAlt(UIEvent)` | `0x7C99A0` / `0x7C9910` | Toggle static flags, then rebuild the keyboard. |
| `releaseModifiers(Document)` | `0x7C96C0` | Restores modifier state and display; exact point in key lifecycle needs testing. |
| `addCommonPhrase(UIEvent)` | `0x7C8710` | Adds a preset/common phrase to input. |
| `showCommonPhrases`, `showCommonBugPhrases` | `0x7C9860`, `0x7C97B0` | Alter optional phrase UI; keyboard exposes explicit hide helpers too. |

**Lesson from the code:** the keyboard's state is **static**, not necessarily isolated per menu instance. A mod that launches a keyboard from the auction page and leaves it open while another UI asks for input could have state/focus interactions. Reuse documented native `ShowKeyboard` only after tracing the focus and callback lifecycle; do not assume merely making a keyboard visible guarantees the entered string will reach your input field.

## 5. ObjectOptionMenu builds document choices and delegates their handling

`ObjectOptionMenu.AddChoice(string newChoice,bool isDisabled,Document)` **`0x7C0150`** contains separate branches for enabled and disabled choices, constructing markup and adding it to a document element. The choice method operates on the menu's `parentBehaviour` static reference.

- `ObjectOptionMenu.ClearChoices(Document)` **`0x7C07A0`** resets the displayed choice list.
- `ObjectOptionMenu.handleChoiceClick(UIEvent)` **`0x7C0B10`** extracts the clicked choice from the UI element/class metadata and invokes downstream behavior.
- `ObjectOptionMenu.getDataFromClasses(Element)` **`0x7C0900`** reconstructs dictionary-like data encoded in element class labels.

This shows a reusable pattern of **DOM class metadata → UIEvent → owner MonoBehaviour**. It could guide accessibility overlays or read-only tracing of interactive world menus; verifying the exact parent callback matters before hooking any action.

## 6. Design guidance for community mods

A stable UI mod should:

1. Identify the **specific game build** and current `Document` hierarchy at runtime; do not assume IDs/element names from anonymous native string pointers without resolving them.
2. Subscribe to UI lifecycle events with reversible hooks; unsubscribe on disable and scene/menu close.
3. Separate player-visible item/auction/notification content from server-owned underlying state.
4. Handle long strings, unusual Unicode, escaped markup, null item data, no matching Element and rapidly reopened pages.
5. Prefer verified open-source mod implementations as integration examples, pinning commits and compatible game versions.
6. Avoid treating direct calls at RVAs as stable cross-version APIs.

**Test matrix:** open/close loot menu multiple times, display item stack 1 vs 2, attack-only and armor-only item, switch rarity, enter keyboard text and use shift/alt/numeric/enter, show notification while closing HUD, and send two rapid notifications. The client-only display results should be compared with the authoritative inventory.

**Confidence:** static traces for fields, branch conditions, DOM update patterns and timed callbacks. **Unknown:** full DOM selector names, animation styles, exact `type` tokens, keyboard's app-level submit target and menu creation order in every client build.
