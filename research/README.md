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

## Deep gameplay research (Batch 03)

- [Camera, avatar LOD, scale and scene/prefab boundaries](batch-03-player-camera-and-world.md)
- [Client-to-server requests and component replication](batch-03-server-and-network-contracts.md)
- [Runemage, Bard, Shaman, monster combat and Fisher](batch-03-combat-and-classes.md)
- [Inventory, loot, dungeon events, native UI and weapon adjustment research](batch-03-items-events-ui-and-weapon-adjustments.md)
- [Repeatable deep-research standard and batch-status tracker](batch-research-standard.md)
- [Offline Ghidra metadata audit tool](../tools/ghidra_export_audit_README.md)

**For AI assistants:** choose the subsystem guide, check its snapshot RVA and static/runtime confidence, then follow the documented caller/callee chain. Never treat a visible client-side request as a server-authorized or persistent mutation.
