# AI Agent Instructions — OrbusVR Modding

This repository is a navigation and research resource, **not** a substitute for checking actual game assemblies and current mod source.

## Start here
1. Read [README.md](README.md) and [docs/getting-started.md](docs/getting-started.md).
2. Identify whether the requested work is a client BepInEx plugin, server plugin, or external desktop tool.
3. Read [docs/architecture.md](docs/architecture.md), [docs/modcore-integration.md](docs/modcore-integration.md), and [references/open-source-mods.md](references/open-source-mods.md) as relevant.
4. Consult the linked live source repository for working code. Pin a commit when reproducing behavior.
5. For game internals, use [research/README.md](research/README.md). Never invent class names, signatures, offsets, hooks, or configuration APIs.
6. Document the exact client build, loader/runtime, dependencies, and test steps for every change.

## Evidence standards
- **Verified**: confirmed by a cited source file, symbol dump, or reproducible test; record the game build and evidence.
- **Observed**: reported in a log or experiment, not yet independently reproduced.
- **Hypothesis**: proposed explanation requiring validation.
- **Planned**: design only; not a supported API.

Never present a planned ModCore API as already implemented. Prefer minimal, reversible changes and clear compatibility boundaries. Do not embed proprietary game binaries, private keys, tokens, server credentials, or personal data in generated code or commits.

## Deliverables for a new mod
Explain installation, dependencies, build commands, expected behavior, compatibility, limitations, and a short manual test checklist. Do not assume a plugin is safe on third-party servers; respect server rules and permissions.

## Indexed reverse-engineering references

For a symbol lookup, search [the namespace type index](references/magicalactual-types.tsv), then [core-symbols.json](references/core-symbols.json) for selected signatures, fields and snapshot RVAs. Use [docs/game-systems.md](docs/game-systems.md) as a human overview and [docs/research-workflow.md](docs/research-workflow.md) for validation. Never claim the namespace index is complete across all assemblies. Source snapshot build is currently unverified.

## Decompiled-behavior research navigation

Start with [the eight-batch research standard](research/batch-research-standard.md). For discovered player/camera/world behavior read [this guide](research/batch-03-player-camera-and-world.md); for networking/authority consult [the component contract guide](research/batch-03-server-and-network-contracts.md); for classes and spell input use [combat/class research](research/batch-03-combat-and-classes.md); and for inventory/UI/gear calibration use [items/events/weapon adjustments](research/batch-03-items-events-ui-and-weapon-adjustments.md). The [offline metadata audit tool](tools/ghidra_export_audit_README.md) can recreate call indexes from a matching private export.

**Do not conflate:** function index coverage, static behavior tracing, and runtime verification. Batch 03's analyzed traces are useful starting points, not an exhaustive understanding of 10,000 methods. Retain component scope for method IDs and verify server-side handlers before suggesting authoritative actions.

## Batch 02 native networking research

Use the [Batch 02 deep dive](research/export-batch-02-deep-dive.md) to navigate the [incoming message parser/entity spawn path](research/batch-02-incoming-message-parser-and-spawns.md), [NetEntity callbacks/despawn/interpolation](research/batch-02-component-dispatch-and-entity-lifecycle.md), [connection and scene/prefab lifecycles](research/batch-02-connections-zone-loading-and-prefab-pools.md), [NPC dialogue](research/batch-02-npc-dialogue-interaction-and-ui.md), and [Orbhealer/health-bar presentation](research/batch-02-orbhealer-healthbars-and-combat-ui.md). The [curated method mapping](references/batch-02-curated-methods.json) is a *selected* set, not the whole game's method map. Cross-check snapshot RVAs and do not infer server permission, world-streaming radius, guaranteed casting success or persistent state from client code alone.

## Batch 04 interface, inventory and rendering research

The [Batch 04 deep dive](research/export-batch-04-deep-dive.md) links the [auction request and response trace](research/batch-04-auction-market-contracts.md), [native PowerUI and keyboard methods](research/batch-04-powerui-menus-notifications-and-keyboard.md), [item stats and enhancement fields](research/batch-04-item-stat-and-loot-data-reference.md), [TerrainGrid and NavMesh](research/batch-04-terrain-grid-and-navigation.md) and [ImposterManager/Oculus SDK boundaries](research/batch-04-rendering-impostors-avatars-and-pathfinding-libraries.md). Use [140 curated method declarations](references/batch-04-curated-methods.json) as snapshot-specific starting points, not a complete API. Do not conflate SDK inclusion with active game usage, visual loot display with server item creation, grid display meshes with terrain streaming, or client auction requests with successful trades.

## Capture mission definitions and weighted progress

[Server-derived capture mission research](research/mission-capture-weights-and-reward-tiers.md) explains why checklist `timesToKill` is not the next reward target, documents rare critter values (1 versus 3 points), and links the 16-definition [QuestHelper objective atlas](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/capture-mission-definitions-20261109/references/capture-objectives-2026-11-09.json). Descriptions and type identify records when the server definition has no explicit mission ID. Exact ID correspondence and runtime tier-reset semantics remain unverified.

## Monster, Fishing, Jester and Event mission research

[170 source-derived mission definitions](research/missions-monster-fishing-jester-event.md) cover 58 Monster, 41 Fishing, 31 Jester and 40 Event quests, including multi-target enemy lists, fish weight vs fish count, potion brewing vs consumption, and Gold-standard event completion. See [the derived machine-readable objective atlas](https://github.com/Hor1zonVR/OrbusQuestHelper/blob/feat/priority-mission-definitions-20261109/references/priority-missions-objectives.json) and [QuestHelper PR #4](https://github.com/Hor1zonVR/OrbusQuestHelper/pull/4). These are source-backed static facts; per-player mission progress and live request handling still need runtime verification.
