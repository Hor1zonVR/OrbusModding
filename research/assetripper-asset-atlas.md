# AssetRipper asset atlas — RC-first modding research

**Status (2026-11-25):** initial metadata-only index, not a reconstructed source-code project or proven runtime API. This complements the existing IL2CPP/Ghidra research. Keep original Unity game files, meshes, textures, icons, scene files and shaders locally. Do not publish raw game content without appropriate rights.

## How to generate it

Use `tools/build_asset_atlas.py` with Python 3 (standard library only). Each input is optional, but at least one is required:

```powershell
py -3 .\tools\build_asset_atlas.py `
  --images "C:\path\to\OrbusImageCatalogue.csv" `
  --collection "C:\path\to\Highsteppe_level5.txt" `
  --assets "C:\path\to\ExportedProject\Assets" `
  --out "C:\OrbusResearch\AssetAtlas"
```

Outputs:

- `icons.csv`: local paths and **guessed** item/category/class hints inferred from image filenames.
- `scene_collection.csv`: Path ID, class and object name from the supplied AssetRipper collection. **A Path ID is collection-scoped, not a global item ID.**
- `replay_scene_candidates.csv`: potential Highsteppe terrain/scenery GameObjects for RebornCamera inspection.
- `rig_weapon_candidates.csv`: potential grip/rig/weapon objects for WeaponAdjustments inspection.
- `project_files.csv`: optional paths to recovered Unity scenes, prefabs, shader files, and model-related files. Path existence does not prove a usable dependency or live loading.
- `summary.json`: counts and warnings.

The script **does not copy game asset bytes**. Its classifications are search filters, not authoritative relationships. When adding curated findings, record client build, source collection, exact hierarchy path, live observation and confidence.

## Evidence to date

- The user's AssetRipper `level5` list associated with `ZoneHighsteppe` contains **42,052** rows including **11,747 GameObjects**, **6,271 MeshFilters** and **1,237 LODGroups**.
- The image catalogue contains **4,458** image paths, including **1,315** under `Resources/ui_icons/inv` and **1,256** under `Resources/ui_icons/weapons_and_armors`.
- A reconstructed `ZoneHighsteppe` scene can be inspected in **Unity 2018.4.30f1**. Several AssetRipper placeholder Orbus shaders were replaced with experimental approximations, making terrain/tree/building surfaces visible in the Unity editor.
- A `Coliseum` scene asset was seen in the export. Its actual hierarchy, lighting, collisions and suitability for runtime loading **have not yet been tested**.

These are static export/editor observations, not proof that private servers will load arbitrary zones or that offline replay can simply import exported scenes.

## 1. RebornCamera — immediate priority

A useful first milestone is **one short, persistent Highsteppe replay**, not a full game rebuild:

1. Select one landmark, character rig and weapon. In Unity, record **GameObject hierarchy paths, transform relationships, mesh/material identities, renderer state, LODGroups** and any collider data.
2. Cross-check **live client** object names/identities. RebornCamera currently caches some nearby renders *in memory*, while its offline viewer uses a generated environment. The exported scene is an offline research source, not a plug-in replay renderer.
3. Record **30 seconds** of player head/hands/body and a few known nearby objects, with explicit scene/zone boundaries.
4. Serialize stable scene/object references and test playback after **game restart**. Record missing/streamed objects as missing; do not invent poses or distant geometry.
5. Build cinematic freecam/timeline UI on top of that verified, persistent foundation.

Related research: [camera/player/world](batch-03-player-camera-and-world.md) and [scene/prefab pools](batch-02-connections-zone-loading-and-prefab-pools.md).

## 2. WeaponAdjustments — next priority

Inspect class-specific weapon meshes and their **grip/controller/hand hierarchy**, including transforms/rotation/scale and prefab variants. Then compare against the actual *live* grip bridge. A static mesh pivot **is not necessarily** the native weapon grip offset. Use this information to help validate "Original" baseline preset behavior and give more useful model-backed visual previews. Preserve Community Edition versus obfuscated Renewed compatibility and do not commit guessed write methods.

## 3. OrbusWorlds — later, with the Coliseum as a reference

Earlier goal: Unity 2018.4 AssetBundle maps, browser/versioned downloads, private-server sessions, collision and multiplayer synchronization, eventually PvP arenas, wave survival, escape rooms and dungeons. Start with **a tiny independently authored arena** and demonstrate two-player synchronized visibility, collision and shared session behavior. The recovered Coliseum is a research reference, **not proof of runtime map support** or permission to redistribute game models.

## 4. RebornManager — lower priority

RM already supports locally selected icon folders and item thumbnails. Reuse verified icon metadata later; avoid diverting camera/weapon research into a large RM redesign.

## Publishing and confidence

Follow [research/README.md](README.md). Label findings **Verified / Observed / Hypothesis / Planned** and distinguish game/export/editor evidence from runtime tests. Don't upload full third-party scenes, materials, or proprietary bundles into this repository.