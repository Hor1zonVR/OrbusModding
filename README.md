# OrbusModding

**AI-readable OrbusVR modding knowledge base and developer starter resources.**

This independent community project documents OrbusVR client and server modding research, including IL2CPP/Ghidra findings, BepInEx workflows, Unity behavior, settings integration, and practical examples.

> **Early foundation:** This repository currently contains a documentation skeleton and links to public projects. The reverse-engineering index and compile-ready templates are being validated. Do not treat unverified notes as stable APIs.

## For AI coding assistants
Start with **[AGENTS.md](AGENTS.md)**. Read the topic guides, then inspect the linked public source projects. Verify signatures and version compatibility before writing patches.

## For developers
- [Getting started](docs/getting-started.md)
- [Architecture and compatibility](docs/architecture.md)
- [ModCore / RebornMenu integration](docs/modcore-integration.md)
- [Reverse-engineering research](research/README.md)
- [Open-source mod examples](references/open-source-mods.md)
- [Basic BepInEx starter guidance](templates/basic-bepinex/README.md)

## Contributing research
Each finding should state the client build, evidence, confidence, limitations, and reproduction steps. Original research is welcome. Avoid uploading proprietary game binaries, private dumps, credentials, or personal data.

## Scope
This is an independent community project, not official OrbusVR documentation. Respect the rules of servers you join and the rights of third-party software authors.

## Reverse-engineering reference (first snapshot)

- [Searchable Orbus namespace type index](references/magicalactual-types.tsv) — 540 `MagicalActual` types from one unverified-build IL2CPP dump.
- [Core symbols for coding assistants](references/core-symbols.json) — selected fields/methods/RVAs from 48 classes.
- [Human-readable game systems map](docs/game-systems.md) — starting points for player, combat, networking, inventory and movement research.
- [Research snapshot and caveats](research/il2cpp-snapshot.md)
- [Ghidra and IL2CPP workflow](docs/research-workflow.md)
- [Regenerate indexes locally](tools/index_il2cpp.py) — no original game dump needs to be committed.

The index is **metadata only**, not proof of functionality, runtime compatibility, or permission to use a network method on third-party servers.
- [Native symbol cross-check (585 of 585 matched)](research/native-crosschecks.md) and [verification tool](tools/verify_il2cpp_signatures.py).

## Ghidra export research (November 2026)

- [Batch 1: native/IL2CPP infrastructure overview](research/export-batch-01-overview.md)
- [Batch 2: networking, scenes, NPCs, class mechanics and remote entities](research/export-batch-02-deep-dive.md)
- [Batch 3: gameplay, external-camera limit, player LOD and network requests](research/export-batch-03-deep-dive.md)
- [Batch 4: auctions, PowerUI, item metadata, NavMesh and rendering](research/export-batch-04-deep-dive.md)
- [Full-export research priority map](research/full-export-priorities.md)
- [Curated cross-system Ghidra behavior map](research/ghidra-behavior-map-2026-11-08.md)

These are evidence-labeled static findings from an **unverified-build** snapshot, not stable server APIs. Private decompiler exports and full pseudocode are not redistributed.

## In-depth reverse-engineering guides

- **[Research standard for all eight export batches](research/batch-research-standard.md)** — coverage criteria, confidence levels, next investigations.
- **Batch 02:** [incoming message parser/entity spawning](research/batch-02-incoming-message-parser-and-spawns.md) · [component dispatch and entity lifetime](research/batch-02-component-dispatch-and-entity-lifecycle.md) · [ENet connection/scene/prefab pools](research/batch-02-connections-zone-loading-and-prefab-pools.md) · [NPC dialogue](research/batch-02-npc-dialogue-interaction-and-ui.md) · [Orbhealer and health bars](research/batch-02-orbhealer-healthbars-and-combat-ui.md).
- **Batch 04:** [auction and market](research/batch-04-auction-market-contracts.md) · [terrain/navmesh](research/batch-04-terrain-grid-and-navigation.md) · [PowerUI](research/batch-04-powerui-menus-notifications-and-keyboard.md) · [equipment stats](research/batch-04-item-stat-and-loot-data-reference.md) · [impostor/SDK research](research/batch-04-rendering-impostors-avatars-and-pathfinding-libraries.md) · [140 curated method references](references/batch-04-curated-methods.json).
- **Batch 03:** [camera/player/world](research/batch-03-player-camera-and-world.md) · [network and server boundaries](research/batch-03-server-and-network-contracts.md) · [classes and combat](research/batch-03-combat-and-classes.md) · [inventory/events/UI/weapon adjustments](research/batch-03-items-events-ui-and-weapon-adjustments.md).
- [Full Batch 03 starting overview](research/export-batch-03-deep-dive.md) and [all-batch priority map](research/full-export-priorities.md).
- [Offline Ghidra metadata auditor](tools/ghidra_export_audit_README.md) — regenerate metadata from your own matching export without publishing its decompiled code.

[Contribute a verified finding](research/CONTRIBUTING_FINDINGS.md) · [Machine-readable research progress](references/research-batches.json).

**Research status:** batches 2, 3 and 4 have detailed, selected subsystem traces, but neither batch nor the entire 79,754-function export is exhaustively understood or runtime-verified. All static findings are build-specific leads, not promises of supported mod APIs.
