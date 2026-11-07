# ModCore / RebornMenu integration

The goal is a shared in-game **Mods** configuration page, rather than every mod implementing its own independent overlay.

**Status: API contract pending verification.** RebornMenu has existing public source code; the planned ModCore consolidation and registration interface must not be assumed complete.

## Integration checklist
1. Inspect the current [OrbusRebornMenu source](https://github.com/Hor1zonVR/OrbusRebornMenu).
2. Identify the exact plugin version and exposed configuration/registration methods.
3. Confirm initialization order, optional dependency behavior, persistence, and supported controls.
4. Use a fallback or disable settings gracefully if the dependency is absent.
5. Test navigation, VR pointer interaction, saving, and client restart.

When a stable ModCore API is published, replace this checklist with verified C# snippets pinned to a release or commit.
