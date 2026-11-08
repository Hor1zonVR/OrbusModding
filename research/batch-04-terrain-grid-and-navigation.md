# Batch 04 — TerrainGrid, TerrainCell and navigation checks

**Game snapshot:** user-generated Ghidra IL2CPP export, function ordinals 30,001–40,000. **Base:** `0x180000000`; exact build unverified. Decompiler interpretation: **static-traced**, not runtime-tested.

This page addresses a common reverse-engineering trap for camera, locomotion, teleportation and world-building mods: **`TerrainGrid` is not necessarily the actual game-world terrain streamer.**

## 1. What the real `TerrainGrid` object contains

The managed class `TerrainGrid : MonoBehaviour` (`TypeDefIndex 7105`) has:

| Field | Offset | Research significance |
|---|---:|---|
| `cellSize` | `0x18` | Width/depth spacing for navigation cells |
| `gridWidth` / `gridHeight` | `0x1C` / `0x20` | Grid dimensions |
| `yOffset` | `0x24` | Vertical adjustment |
| `cellMaterialValid`, `cellMaterialInvalid` | `0x30`, `0x38` | Distinct visual materials for valid vs invalid cells |
| `outlineMaterial` | `0x40` | Grid outline presentation |
| `TerrainCell[] _cells` | `0x48` | Object-level validity and position records |
| `float[] _heights` | `0x50` | Cached per-grid-point vertical values |
| `gridDisplay` | `0x60` | Grid visualization object |
| `navigationJumps` / `taxiExitJumps` | `0x68` / `0x70` | Navigation/jump waypoint visual objects |
| `latestCols` / `ignoreEnemyCols` | `0x78` / `0x80` | Collider-query caches/filters |
| `currentNavmeshPosition` | `0x98` | Most recently sampled valid NavMesh position |
| `vertices` / `indices` | `0xA8` / `0xB0` | Generated **grid visualization mesh**, not the full world terrain |
| `_NavAreaMask` | `0xB8` | Unity NavMesh area mask |

`PlayerCharacter` separately exposes a `TerrainGrid myGrid` field (snapshot offset **`0x88`**) and `GameObject terrainGrid` (**`0x80`**). This establishes a player-level relationship, not automatically global terrain streaming.

## 2. Native control flow: moving the grid requires NavMesh sampling

**`TerrainGrid.GridMoved(Vector3 newPosition)` — RVA `0x6D73A0`**

- Passes the new position to **Unity `NavMesh.SamplePosition`** (`RVA 0x1417A30`), with **max distance 2.0** and the grid's `_NavAreaMask`.
- When sampling succeeds, obtains the nearest NavMesh point; otherwise the code follows a fallback vector path.
- Writes `currentNavmeshPosition` at `+0x98`.
- Calculates grid-relative offsets using `cellSize`, `gridWidth`, `gridHeight` and the incoming world position.
- Walks its grid's cell objects to update positions and invalidate cached check state so a new query can run.

**Confidence:** the `NavMesh.SamplePosition` identity is cross-checked against the IL2CPP dump, not guessed from anonymous `FUN_` naming. Whether every scene has a suitable NavMesh or the grid is always enabled remains a runtime question.

## 3. TerrainCell checks walkable/colliding space; they don't fetch terrain bundles

**`TerrainCell.doCheck()` — RVA `0x6D5C80`**

The method reads `TerrainCell.myGrid` (**`+0x38`**), this cell's coordinates and collider/object references. A nested loop inspects nearby grid points and consults the `_heights` cache. When a height has not yet been resolved, it performs a **Unity physics raycast** (native `Physics.Raycast` at **`0x13ED930`**) and caches the resulting vertical value relative to the grid origin. The raycast-miss branch writes **-1000.0** to the cached height; that is a sentinel value in this snapshot, not a genuine terrain height.

After adjacent-cell checks, it calls **`UnityEngine.AI.NavMesh.Raycast`** (`0x14179A0`) to compare reachable NavMesh points. Its boolean result feeds `TerrainCell.isValid`.

**`TerrainCell.setNeedsCheck()` — `0x6D6570`** clears a cached check flag.  
**`TerrainCell.get_isValid()` — `0x6D64F0`** returns/caches validity based on that check path.

The combination of raycasts, NavMesh and invalid/valid materials strongly supports **a local navigation/occupancy grid**, rather than a world asset loader.

## 4. Ground, occupancy and grid visualization methods

| Method | RVA | Static evidence |
|---|---|---|
| `TerrainGrid.findGroundAtPosition(Vector3)` | `0x6D8A20` | Performs a downward-oriented physics raycast in the queried scene, returns ground height on hit; the no-hit branch returns float **1000.0** in the inspected pseudocode. Confirm real-world meaning before using the fallback. |
| `TerrainGrid.isSpaceUnoccupied(Vector3,float)` | `0x6D8BA0` | Makes a Unity physics overlap/box query around the supplied position/box size; returns whether the queried collider result is absent. |
| `TerrainGrid.validCellAtPosition(Vector3)` | `0x6D8CC0` | Converts a world-space position into grid-relative integer cell coordinates, checks bounds and returns the selected `TerrainCell.isValid` (after cached check). |
| `TerrainGrid.UpdateHeights()` | `0x6D8430` | Clears/resets entries in the cached `_heights` array. |
| `TerrainGrid.UpdateCells()` | `0x6D8290` | Iterates grid cell dimensions, updates cell-object transforms, and resets their check state. |
| `TerrainGrid.CreateMesh()` | `0x6D6F60` | Allocates a Unity `Mesh`, assigns arrays/bounds data for the **grid display**. |
| `TerrainGrid.UpdateMesh(Mesh,int,int)` | `0x6D84C0` | Updates vertex data for a cell/mesh segment and triggers mesh updates. |
| `TerrainGrid.CombineMeshes()` | `0x6D67F0` | Processes per-cell mesh objects and combines them for efficient visualization. |
| `TerrainGrid.BuildOutGridByPercentage(float)` | `0x6D6600` | Iterates cells with a percentage/index threshold, affecting visibility/presentation. |
| `TerrainGrid.UpdateNavigationJumps()` | `0x6D8720` | Refreshes `navigationJumps`/`taxiExitJumps` collections and their presentation. |
| `TerrainGrid.OnDisable()` / `OnEnable()` | `0x6D7940` / `0x6D7B90` | Scene/lifecycle hooks to investigate when the navigation overlay becomes active. |

### Where this helps, and where it doesn't

**Useful for:** valid teleportable spots, client-side navigation visualization, collision-safe spectator placement previews, accessible path guides, and visual diagnostics for navmesh holes. In a private test, compare `validCellAtPosition` with actual permitted player teleportation; the server may impose **additional** restrictions.

**Not proven:** remote terrain/mesh loading, remote NPC interest radius, full scene asset streaming, all hitboxes, authoritative teleport permission, real collision geometry generation. The mesh created by `TerrainGrid.CreateMesh` is a small navigation-display mesh, **not** a substitute for missing dungeon floors/walls in RebornCamera.

## 5. Distinguish three navigation technologies

- **`TerrainGrid` / `TerrainCell`:** game-specific overlay/sample grid with local NavMesh and physics tests.
- **`UnityEngine.AI.NavMesh`:** engine-provided navigation query API; e.g., `SamplePosition`, `Raycast`.
- **`AstarPath`**, a separate pathfinding graph library included in the binary (e.g. `AstarPath.GetNearest`, `ScanLoop`, `FloodFill`): may be used for some AI/path planning, but **no active gameplay caller has been proven in this pass**.

Do not conflate these systems, and do not treat the mere presence of the A* library as proof every monster uses it.

## 6. Reproducible testing plan

1. On a private instance, locate `PlayerCharacter.myGrid` and inspect the grid's current dimensions and `currentNavmeshPosition`.
2. Walk, teleport and climb while logging `GridMoved`, `UpdateCells`, `TerrainCell.doCheck` and the actual NavMesh/raycast outcomes. Avoid modifying scene collision.
3. Test a valid floor, raised ledge, steep cliff, water and obstructed corner for false positives and the **1000 / -1000** fallback/sentinel values.
4. Move only a spectator camera and observe whether this grid follows the camera or remains bound to the player. This distinguishes spectator preview support from remote world streaming.
5. Cross-check results against the game's actual movement permission and scene-object availability.

**Status:** grid fields, NavMesh/Physics calls and local mesh visualization are statically supported. Runtime behavior, distance limits and server checks remain unresolved.
