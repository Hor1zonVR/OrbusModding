# Batch 02 — Orbhealer/Musketeer-related combat and health-bar UI

**Source:** original Ghidra pseudocode for functions 10,001–20,000, joined with the user-supplied IL2CPP method metadata. **Snapshot:** RVA base `0x180000000`, client build unverified. **Evidence class:** static-analysis traces. Do not assume a native method name represents a safe public BepInEx API.

## 1. The internal `Orbhealer` class is a combat-component cluster

The IL2CPP name `MagicalActual.Orbhealer` occurs across the class's bow/orb/turret interaction code. This is relevant to Musketeer-oriented mods even though the native class name does not literally say “Musketeer.”

| Named method | RVA | What static analysis supports |
|---|---|---|
| `Orbhealer.Awake()` | `0x2FC2F0` | Initializes local-only object references, equipment/weapon controller references, orb arrays, projectile presentation references and interaction state. Contains substantial defensive IL2CPP array/index checks. |
| `Orbhealer.ClassEnabled()` | `0x2FC8C0` | Per-class activation path. |
| `Orbhealer.FireArrow(Vector3,Vector3,byte,byte,int)` | `0x2FD0C0` | Produces local projectile/weapon presentation, tracks a spell/arrow identifier, and updates locally controlled weapon state. Exact damage/acceptance occurs elsewhere. |
| `Orbhealer.DLSPERSDFA(ushort,Vector3,int)` | `0x2FC920` | Creates a typed request containing a **16-bit target GUID**, a **3-component position**, and an **arrow identifier**, and sends **Orbhealer component method 5** via `NetEntity.CallServerComponent` **`0x2F2910`**. |
| `Orbhealer.SpawnOrb(int,byte)` | `0x2FECC0` | Updates a local array-backed orb representation, with a special spell ID **99** handled as a sentinel in a branch. This alone is not a server spell grant. |
| `Orbhealer.Start()` | `0x2FFB10` | Sends **Orbhealer component method 2** in the observed startup branch; also resets several local timers/flags. |
| `Orbhealer.UpdateLifewellOrb()` | `0x300F60` | Moves/updates a local Lifewell orb and, in a conditional interaction branch, sends **Orbhealer component method 3**. The code also compares a local distance with **0.15 units**. |
| `Orbhealer.doTriggerClick(...)` | `0x301AD0` | Handles trigger/input state, checks locally controlled conditions and can send **Orbhealer component method 4** in a specific branch. |
| `Orbhealer.orbusNetInit(NetEntity)` | `0x3020A0` | Registers replicated variable indices **1–8** and incoming method listener IDs **1–3**. |
| `Orbhealer.FixedUpdate()` | `0x2FD620` | Advances timers, checks ability/orb state and updates visual projectile/indicator objects. Complex input-related state machine. |

### A concrete outgoing request trace

`Orbhealer.DLSPERSDFA(targetGuid, targetPosition, arrowId)` **`0x2FC920`** constructs a short payload object containing position, target ID and arrow ID, then calls `NetEntity.CallServerComponent` with method ID **5** scoped to the **Orbhealer component**.

The send path clears a local state byte at offset `Orbhealer + 0x1D5` after dispatch. It is **not** evidence that a projectile hit or that the server awarded damage. `FireArrow` and local visual instantiation are different milestones.

### Why these matter for mod developers

A useful spectator/analytics overlay should distinguish:

1. **Input press** — controller trigger/gesture state.
2. **Local shot or orb visual** — `FireArrow` or `SpawnOrb` ran.
3. **Outgoing combat request** — `DLSPERSDFA` (method 5) or other class-specific send.
4. **Replicated state** — one of the 8 sync-variable slots changes.
5. **Confirmed combat result** — incoming damage/healing event or server combat log.

Without that distinction, a “shots hit” counter can overcount attempts, and a DPS graph can show results that the server never accepted.

**Unknowns:** arrow ballistics, turret stat inheritance, hit validation, Lifewell healing values, orb cooldowns and exact server damage formulas. Investigate the receiving server handler or an authoritative combat log before publishing numerical values.

## 2. Native `OrbusHealthBar` is substantially more than a percentage fill

Important method map:

| Method | RVA | What it controls or derives |
|---|---|---|
| `OrbusHealthBar.DoViewUpdate()` | `0x3039B0` | A large (~22.7 kB) view-builder that composes title/name text, ratings, quest indicators, health bar/UI elements and branches on target type and visibility. |
| `OrbusHealthBar.FixedUpdate()` | `0x304B10` | Visibility and position updates, fill-ratio transitions, geometry/scale and target-display refresh decisions. |
| `OrbusHealthBar.CompleteName(bool)` | `0x303850` | Provides display-name formatting. |
| `OrbusHealthBar.CheckKillMissionMonster()` | `0x303660` | Looks for kill-mission relevant state through current player/target objects and mission references. It is a UI/mission-indicator check, not quest-reward authority. |
| `OrbusHealthBar.GetKillMissionIndicator()` | `0x305640` | Provides a kill-mission indicator string depending on target/mission conditions. |
| `OrbusHealthBar.GetPlayerTitle(bool)` | `0x305710` | Formats a stored player-title string with optional styling. |
| `OrbusHealthBar.GetTargetSymbol(byte)` | `0x3057D0` | Chooses one of the known target-symbol text variants from an incoming byte. |
| `OrbusHealthBar.RelativeRatingForCurrentPlayer()` | **`0x305820`** | Chooses a textual threat/rating label based on the target's level versus the viewer's level, target flags and player class state. |
| `OrbusHealthBar.showBar()` | `0x3065D0` | Sets visibility flag `+0xA9 = 1` and view-dirty flag `+0x100 = 1`. |
| `OrbusHealthBar.hideBar()` | `0x3063B0` | Sets visibility flag `+0xA9 = 0` and view-dirty flag `+0x100 = 1`. |

### Newly extracted: level-difference threat categories

In the relevant branch of `RelativeRatingForCurrentPlayer()`, the code computes

`difference = targetLevel - currentPlayerLevel`.

It then selects one of **five** string categories by comparing the difference to thresholds:

| Difference | Native branch |
|---|---|
| `< -3` | first tier |
| `-3` or `-2` | second tier |
| `-1, 0, +1` | third tier |
| `+2, +3` | fourth tier |
| `>= +4` | fifth tier |

**Caveat:** the actual displayed localized strings were not resolved from `stringliteral.json`; don't invent the visible text or assert every target always uses this branch. Some targets take alternate rating paths based on status flags and avatar comparison.

The same method distinguishes different target kinds, and its branches manipulate a related UI emphasis/style value (observed 16.0 versus 22.0). These are **UI presentation rules**, not damage multipliers.

### The health bar has a dirty/refresh model

The tiny `showBar()` and `hideBar()` methods simply flip **one visible state flag** and mark the UI **dirty**, leaving actual rendering to update functions. That is an important detail for modders: calling a show/hide helper does not necessarily create a UI element immediately, especially if the target is not currently present or the scene has unloaded.

## 3. Practical public mod ideas

- **Accurate difficulty labels:** read the level-difference tiers for a user-facing UI enhancement; verify the player's active-class level and target state.
- **Quest-target highlight:** hook the kill-mission indicator result, not the actual quest reward logic. If markers are missing, trace `CheckKillMissionMonster` and the mission tracker independently.
- **Musketeer shot diagnostics:** log local arrow visual, outgoing method 5 and server combat result as distinct counters. Provide an option to suppress overlays in VR.
- **Non-invasive accessibility:** use the native health-bar state transitions to observe target changes and render a separate, appropriately sized UI element; avoid overriding authoritative health values.

**Runtime tests needed:** a player switching classes, targets of levels -4 to +4 relative to the player, multiple quest monsters, target death/despawn, Musketeer shots that deliberately miss, and Lifewell orb interactions. Use only a controlled test environment.

## 4. Confidence and open questions

**Static-traced:** request method IDs on the listed call sites, listener/sync registration counts, view dirty flags, five-tier level-difference branch. **Not proven:** exact localized strings, server spell calculations, hit validation, whether display changes apply to every client version, and persistent mission rewards. Build-specific RVAs are not stable APIs.
