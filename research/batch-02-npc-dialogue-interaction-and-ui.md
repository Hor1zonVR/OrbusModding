# Batch 02 — NPC dialogue, interactions and native presentation

**Provenance:** Ghidra pseudocode plus IL2CPP method-name metadata from an OrbusVR `GameAssembly.dll` snapshot; image base `0x180000000`, exact build unknown. All findings below are **static tracing**, not a shipped mod API or runtime-confirmed behavior.

## 1. NPC interaction is deliberately throttled

`MagicalActual.Npc.PlayerInteraction()` **`0x2F79D0`** stores a previous interaction time at native field **`Npc + 0x7C`**. The inspected branch returns early when the elapsed time since the last interaction is **less than 2.0 seconds**.

After passing the local time guard, this method checks a combination of NPC state and nearby UI/interaction references, then either:

- repositions or reveals the NPC dialogue UI through `Npc.PositionDialogue()` **`0x2F7BC0`**;
- calls a world-object/interaction helper on an active component; or
- invokes a player method at **`PlayerCharacter + RVA 0x378710`** passing the NPC's **16-bit entity ID** from its `NetEntity + 0x10`.

The downstream player method `0x378710`, in Batch 03, creates a player-entity component request using method ID **`0x1B` (27)** after additional local checks.

**Implications:** clicking an NPC is not equivalent to a guaranteed dialogue event. There are local cooldown, UI and player-state gates, followed by a server-mediated interaction request in at least one branch.

**Do not claim** that bypassing the local 2-second guard bypasses server interaction cooldowns, distance checks or quest permissions; this has not been demonstrated.

## 2. NPC replication uses discrete incoming method listeners

`Npc.orbusNetInit(NetEntity)` **`0x2FA060`** stores the `NetEntity` reference in native field `Npc + 0x20`, then registers incoming method listener IDs **1, 3, 4, 5 and 6**. Each registration has an argument-schema list and callback/delegate; these are **incoming listener registrations**, not outgoing commands. The absence of an explicit registration for 2 in this initializer must not be interpreted as an exploitable or hidden method.

For precise replay or dialogue overlays, trace the individual callbacks to establish which ID updates dialogue text, choices, emotional animation or shouting. The registration counts alone do not prove that mapping.

## 3. Dialogue widgets are transient scene objects

Useful method map:

| Method | RVA | Static observation / purpose |
|---|---|---|
| `Npc.PositionDialogue()` | `0x2F7BC0` | Repositions dialogue UI relative to the NPC/player context. |
| `Npc.UpdateDialogBox()` | `0x2F9B60` | Compares current player position with a stored dialogue anchor; when the distance exceeds **0.2 units**, may reposition a dialogue object and update the stored anchor. This is a display-follow rule, not an interaction range. |
| `Npc.FixedUpdate()` | `0x2F7620` | Advances NPC presentation: dialogue/shoutbox state, transform positioning and player-relative UI behavior. |
| `Npc.SpeakSetupBox(DialogueBox,string)` | `0x2F8C60` | Builds/updates a text box for incoming dialogue presentation. |
| `Npc.SpeakSetupChoiceOne(string)` | `0x2F8D00` | Displays one choice; additional methods may handle other choices elsewhere. |
| `Npc.Shout(string)` | `0x2F80B0` | Creates/activates a shout widget, sets the text and hides other nested elements. |
| `Npc.SpeakHandleEmotion(string)` | `0x2F8420` | Handles a string-driven emotion/presentation state. |
| `Npc.PromptClickChoice(string)` | `0x2F7FF0` | Checks the chosen string against known values, manipulates a local dialogue option component, then releases the current world menu via `PlayerCharacter.ReleaseInteractionMenu` **`0x380F90`**. |
| `Npc.ClearDialogue()` | `0x2F7060` | Explicit dialogue-state/cleanup path. |
| `Npc.FinishSpeak()` | `0x2F71A0` | Finishing a speech/presentation sequence. |

Note the difference between **dialogue placement/motion thresholds** (e.g. 0.2) and actual gameplay interaction limits (not established by this branch). Likewise, a clicked choice locally closes or changes UI; server quest-choice handling may be in a different function.

## 4. Example: a read-only NPC dialogue transcript mod

A legitimate community mod could record **only dialogue shown to the local player**, with opt-in, local-only storage and no other players' identifiers:

1. Detect a listener invocation through the component dictionary at `NetEntity + 0x90`, verify NPC type and callback ID.
2. Compare the resulting `SpeakSetupBox` / `SpeakSetupChoiceOne` text with what the game displayed.
3. Record a timestamp, NPC display label where permitted, scene identity and dialogue string.
4. Observe `PromptClickChoice` separately to identify *local UI selection*, and wait for an actual replicated update before labelling a quest step completed.
5. Destroy/clear custom UI when `Npc.ClearDialogue`, `FinishSpeak`, `OnDestroy` or a scene transition occurs.

**Do not** construct outgoing quest-choice packets from guesses about string values or listener IDs. Real quest decisions and rewards require the authoritative server handlers.

## 5. Test scenarios

- Click the same NPC twice within two seconds and again after two seconds. Log UI state and actual player-component request calls independently.
- Move the player a small distance while dialogue is visible and monitor whether UpdateDialogBox shifts the widget.
- Test an NPC with multiple choice options and a shoutbox. Record what callbacks **actually** fire.
- Leave the scene while a dialogue box is visible and verify that transcript/hooks do not retain stale references.

**Confidence:** native static control-flow traced for local throttle, listener registration and named UI call paths; exact listener-ID semantics, server choice verification and persistent quest state are **unresolved**.
