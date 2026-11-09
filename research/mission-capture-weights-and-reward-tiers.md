# Capture-mission reward progression and weighted critters

**Source:** 16 Reborn-server capture mission definition records shared by an OrbusVR player on 2026-11-09. **Scope:** source-provided descriptions, template IDs/values, zones and tier requirements, not a client or server runtime trace. **No mission IDs were present.**

## What the fields mean for mod authors

- `type: "capture"` describes the mission activity.
- `checklist.ids` lists creature template IDs and their individual contribution values; for example `mouse` contributes **1** point and `mouse-rare` contributes **3**.
- `checklist.zones` limits where captures count. An empty `ids` list allows any eligible critter in that zone; an empty `zones` list removes that zone restriction in the supplied definition.
- `checklist.timesToKill` can be **100** or **10,000** even when Bronze/Silver/Gold rewards require much less. It must not automatically be used as the player's **next reward target**.
- `bronze.requirement`, `silver.requirement`, `gold.requirement` are supplied as **per-tier requirements**. For a cumulative progress counter, the next milestones are Bronze, Bronze+Silver and Bronze+Silver+Gold. Recheck semantics when the game resets mission progress after turning in a reward.
- `Mission.id` is a distinct runtime field; do **not** invent a `captureN` identifier by array order. Description/type matching can identify these 16 descriptions without an ID, but it is version-specific.

## Supported examples

| Mission | Zone / eligible template | Bronze | Silver adds | Gold adds | Cumulative milestones |
|---|---|---:|---:|---:|---|
| Market mice | `ZoneHighsteppe`; `mouse:1`, `mouse-rare:3` | 6 | 3 | 5 | 6 / 9 / 14 |
| Parathime Finches | `Zone3`; `bird:1`, `bird-rare:3` | 6 | 3 | 5 | 6 / 9 / 14 |
| Obnobi Lizards | `Zone4`; `lizard:1`, `lizard-rare:3` | 10 | 8 | 12 | 10 / 18 / 30 |
| Green Crested Fowl | `Zone1`; `bird2:1`, `bird2-rare:3` | 8 | 6 | 6 | 8 / 14 / 20 |
| Hulthine's Basin birds | `Zone2`; `bird3:1`, `bird3-rare:3` | 6 | 5 | 6 | 6 / 11 / 17 |
| Hairless skunks | `Zone5`; `corrupt1:1`, `corrupt1-rare:3` | 8 | 5 | 8 | 8 / 13 / 21 |
| Mutated toads | `Zone5`; `corrupt2:1`, `corrupt2-rare:3` | 8 | 5 | 8 | 8 / 13 / 21 |
| Lizards and toads | Anywhere; `lizard:1`, `corrupt2:3` | 10 | 8 | 8 | 10 / 18 / 26 |

**All 16:** The [full community capture-objective reference](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/capture-mission-definitions-20261109/references/capture-objectives-2026-11-09.json) includes exact description-match prefixes, original zone IDs, template IDs and weighted values, and per-tier totals. The [QuestHelper research notes](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/capture-mission-definitions-20261109/docs/CAPTURE_SERVER_DEFINITIONS.md) explain how to use it without guessing IDs.

## Implications for reliable client-side QoL mods

For a tracker, read `Mission.progress`, `ChecklistItem.killCount` and native reward tiers from the live game object. These are **server-owned changing counters**. Use static definitions only to label the objective or provide an explicitly version-matched fallback tier when native data is missing. Weighted capture points are not necessarily individual animals caught.

**Status:** definitions received from the user, with the 16 records transcribed as independently written metadata and tested by the QuestHelper offline objective-rule project. Exact active-client ID mapping and tier-reset behavior still require runtime validation.
