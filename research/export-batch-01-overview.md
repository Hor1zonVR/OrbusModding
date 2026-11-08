# Full-game decompiler export review — Batch 01 (functions 1–10,000)

**Date:** 2026-11-08. **Source:** Ghidra `GameAssembly.dll` batched export from an OrbusVR IL2CPP snapshot. This is a high-level, independently written research summary; no raw proprietary decompilation is redistributed here.

## Overview

- Entire captured export: 79,754 selected functions, 79,745 successfully decompiled, 9 failures across both runs.
- Batch reviewed here: **indices 1–10,000**, with **10,000 successful decompilations and zero failures**.
- Approximately 6.16 million characters of pseudocode were indexed privately in this batch.
- **33,434 distinct explicit caller-to-callee pairs** were found by scanning direct `FUN_...` calls, of which **11,682** have a callee also present in this batch. This does not include indirect, virtual or reflection-based invocation.
- Source RVA range approximately `0x1000`–`0x13FB60` (snapshot-relative).
- The private index stores pseudocode in SQLite with full-text search, plus address, ordinal, signature text, source filename, and direct call edges. The private index and raw text **are not part of the public repository**.

## Findings and interpretation

1. **This early address range is primarily native/IL2CPP infrastructure and Unity setup**, rather than clearly identifiable Orbus gameplay methods. In this batch, Ghidra gave 9,978 entries generic `FUN_...` names, 19 `thunk_...` names, 2 `il2cpp...` names, and 1 other name. This is a Ghidra labeling limitation, not evidence that the code lacks managed symbols.
2. **String-heavy registration patterns are common.** At least 2,687 functions explicitly call `FUN_1801E5AB0`, often with strings naming modules, assets, attributes or runtime metadata. Examined examples include strings mentioning `UnityEngine.UnityAnalyticsModule`, `UnityEngine.UnityWebRequestWWWModule`, and `Unity.InternalAPIEngineBridge.017`. Seeing module names does not prove a specific Orbus subsystem uses them.
3. **No literal `Orbus` occurs in these 10,000 pseudocode bodies.** Simple keyword classification therefore risks confusing Unity descriptions (e.g. references to weapon, chest, movement) with game-specific logic. Do not publish such matches as confirmed Orbus features.
4. **Practical consequence:** Preserve this batch in the indexed archive for call-graph dependencies; direct behavior investigation should preferentially focus on higher RVAs where the IL2CPP metadata maps named gameplay types such as `PlayerCharacter`, `NetEntity`, `Monster`, `ScenePreloader`, `DungeonShard`, and `BossChest`.

## Method and limitations

The private offline indexer parses the original `functions_XXXXXX-YYYYYY.txt` exports, records virtual addresses/RVAs, extracts visible direct `FUN_` call references, and creates an SQLite full-text index. Counts are automated; **we have not manually understood or runtime-tested every indexed function**. We will apply the same workflow in approximately 10,000-function increments. High-value static findings get their own documented method, caller/callee evidence and confidence level, and must be runtime-tested before being described as verified behavior.

**Next:** Batch 02, indices 10,001–20,000, and continue linking names with the matching IL2CPP metadata.
