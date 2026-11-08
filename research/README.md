# Reverse-engineering research

This directory will hold **original analysis** derived from IL2CPP metadata, Ghidra inspection, runtime tests, and Unity object research.

## Publishing rules
Do not upload raw proprietary game binaries, complete asset bundles, private server material, secrets, or unreviewed dumps by default. Publish curated findings with provenance and rights review.

## Finding template
- **Finding ID**:
- **Topic**:
- **Game/client build**:
- **Tool and version**:
- **Symbol / type / method signature**:
- **Evidence source** (file path, hash, relevant lines or address where lawful):
- **Behavior and limitations**:
- **Confidence**: Verified / Observed / Hypothesis / Planned
- **Reproduction steps**:
- **Related public mod**:

Offsets and addresses are version-dependent. Never reuse an offset from one build without checking it against the target build.

## Current research reports

- [Cross-system Ghidra behavior map](ghidra-behavior-map-2026-11-08.md)
- [Batch 1: functions 1–10,000](export-batch-01-overview.md)
- [Batch 3: functions 20,001–30,000](export-batch-03-deep-dive.md)
- [Priority map for the complete export](full-export-priorities.md)

Static interpretations are not runtime-verified APIs. Check method evidence and build fingerprint before using any address.

## Deep research: menus, auctions and navigation (Batch 04)

- [Batch 04 overview and findings](export-batch-04-deep-dive.md)
- [Auction-house outgoing requests and incoming listing updates](batch-04-auction-market-contracts.md)
- [TerrainGrid, NavMesh and collision tests](batch-04-terrain-grid-and-navigation.md)
- [PowerUI loot lists, keyboard, notifications and object choices](batch-04-powerui-menus-notifications-and-keyboard.md)
- [Item stats, enhancement and durability fields](batch-04-item-stat-and-loot-data-reference.md)
- [Impostor rendering, Avatar SDK and pathfinding boundary notes](batch-04-rendering-impostors-avatars-and-pathfinding-libraries.md)
- [Batch 04 selected AI-readable method reference](../references/batch-04-curated-methods.json)

## Deep networking and game-system research (Batch 02)

- [Full Batch 02 deep-dive and system map](export-batch-02-deep-dive.md)
- [Incoming message parser, spawning, entity update and despawn](batch-02-incoming-message-parser-and-spawns.md)
- [Component network contracts, callback dispatch and remote movement](batch-02-component-dispatch-and-entity-lifecycle.md)
- [ENet connection loops, scene load, prefab pools and player rig](batch-02-connections-zone-loading-and-prefab-pools.md)
- [NPC interaction, dialogue, choices and UI](batch-02-npc-dialogue-interaction-and-ui.md)
- [Orbhealer/Musketeer and health-bar mechanics](batch-02-orbhealer-healthbars-and-combat-ui.md)
- [Machine-readable selected Batch 02 methods](../references/batch-02-curated-methods.json)

## Deep gameplay research (Batch 03)

- [Camera, avatar LOD, scale and scene/prefab boundaries](batch-03-player-camera-and-world.md)
- [Client-to-server requests and component replication](batch-03-server-and-network-contracts.md)
- [Runemage, Bard, Shaman, monster combat and Fisher](batch-03-combat-and-classes.md)
- [Inventory, loot, dungeon events, native UI and weapon adjustment research](batch-03-items-events-ui-and-weapon-adjustments.md)
- [Repeatable deep-research standard and batch-status tracker](batch-research-standard.md)
- [Offline Ghidra metadata audit tool](../tools/ghidra_export_audit_README.md)

**For AI assistants:** choose the subsystem guide, check its snapshot RVA and static/runtime confidence, then follow the documented caller/callee chain. Never treat a visible client-side request as a server-authorized or persistent mutation.

[Batch 02: network request envelope and scene loading (first traces)](batch-02-network-and-scenes-first-traces.md) — connects the gameplay requests in Batch 03 to native serializer and preload methods. This is an initial subsystem analysis, not a complete deep review of Batch 02.
