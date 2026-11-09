# Monster, Fishing, Jester and Event mission definitions — developer reference

**Evidence:** source data from [Community Reborn Server `content/missions` at 330d1e8](https://github.com/OrbusVR-Community/reborn-server/tree/330d1e8934ea5c09e6732c592ce15c4fc09b3b3e/content/missions), independently parsed on 2026-11-09. This snapshot may not match a modified Spades server. These are **server definition facts**, not client runtime verification.

## Dataset

- **MonsterHunter:** 28 repeatable + 30 level = **58** (`kills`, `singlekill`, `killlist`).
- **Fisher:** 27 repeatable + 14 level = **41** (`fishcaught` and `fishcaughtweight`).
- **Jester:** 14 repeatable + 17 level = **31** (`harvest`, `brewpotion`, `consume`, `equipmentsalvage`, `earndram`).
- **EventHelper:** 20 repeatable + 20 level = **40** (`eventparticipation` and `eventgold`).
- Combined **170**; plus [16 earlier capture definitions](mission-capture-weights-and-reward-tiers.md) = **186 researched definitions**, not every historical/seasonal quest.

An independently written, [AI-readable atlas of 170 compact objectives](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/priority-mission-definitions-20261109/references/priority-missions-objectives.json) includes exact source level IDs, activity, target template IDs/weights, zone constraints, sub-objective descriptions when provided, required per-tier increments, cumulative values, and a description fingerprint for records without IDs. It does not copy the server's narrative paragraphs. [Detailed implementation and test notes](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/priority-mission-definitions-20261109/docs/PRIORITY_MISSION_DEFINITIONS.md).

## What modders should learn

### Killlists contain separate quotas

`hunter10` includes **Undead (native checklist target 5), Dungeon Troll (2), Lich King (2)**. A client tracker should render each native checklist entry separately when available, rather than collapsing all of them into a vague `Defeat monsters` counter. Per-entry `timesToKill` of 5/2/2 is not equivalent to a single generic 10,000-count upper bound.

### Fishing has two distinct units

`fishcaught` tracks number of fish; `fishcaughtweight` tracks catch **weight**, with an unspecified physical unit in the source data. Do not label weight as number caught or invent kg/lb units. Example level missions: `fishing9` counts Sunfish (Bronze 9, Silver +5, Gold +7); `fishing6` tracks total catch weight near Highsteppe/Kingsport (15, +10, +20).

### Jester is five different activities

A Jester mission may require harvesting a plant, brewing a named potion, **consuming** a potion, salvaging equipment, or earning a specified amount of Dram. `jester27` brews Runesight Potion (1,+1,+1); `jester29` drinks Ruined Potions in Highsteppe (3,+5,+5).

**Ambiguity:** two repeatable Dram missions have identical text but different tier amounts. They cannot be distinguished by description alone, so a safe client must use actual native reward tier fields.

### Event Gold means award standard, not money

`eventparticipation` requires taking part/completing relevant events; `eventgold` specifically asks for an event finished to **Gold ranking**. For example `event18` concerns Gold-standard completion at Lamavora's ruins (2,+1,+2).

### Stages and server authority

The source's `bronze.requirement`, `silver.requirement` and `gold.requirement` are per-stage increments. The next cumulative reward thresholds are B, B+S, B+S+G **if** live progress is cumulative. Check `Mission.progress` against `ChecklistItem.killCount` and native stage state before showing an absolute target.

`timesToKill=100/1000/10000` is frequently just a checklist cap; don't show `98/10000` as the next reward. Native live mission state is authoritative, bundled metadata is fallback display support, and a server's mission-request method must be separately validated before attempting background refresh.

## Implementations

[QuestHelper draft PR #4](https://github.com/Hor1zonVR/OrbusQuestHelper/pull/4) implements the compact atlas, labels, tier fallback and multi-checklist display. **Offline tests passed**, but the current Spades build and VR HUD are **not yet runtime-tested**, and the older issue of needing to open the Missions tab for server-fresh progress remains unresolved.
