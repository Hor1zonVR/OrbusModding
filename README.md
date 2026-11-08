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
- [Batch 3: gameplay, external-camera limit, player LOD and network requests](research/export-batch-03-deep-dive.md)
- [Full-export research priority map](research/full-export-priorities.md)
- [Curated cross-system Ghidra behavior map](research/ghidra-behavior-map-2026-11-08.md)

These are evidence-labeled static findings from an **unverified-build** snapshot, not stable server APIs. Private decompiler exports and full pseudocode are not redistributed.
