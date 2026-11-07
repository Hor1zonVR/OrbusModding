# Architecture and compatibility

## Known project context
- The OrbusVR client has been investigated using IL2CPP dumps, Ghidra, and Unity asset inspection.
- Historical modding work used Unity **2018.4.30f1** and BepInEx; verify these details against the specific client build.
- Different community clients and instances may differ in symbols, dependencies, and supported behavior.

## Separate concerns
- **Client plugin**: runs in the player's game process; local visuals, UI, and client-observable state.
- **Server extension**: runs on a controlled server and may expose server-authoritative functionality; do not assume client APIs exist server-side.
- **Desktop tool**: manages installations, files, releases, or other external workflows.

Do not assume that client changes replicate to other players, or that server changes can be performed by an ordinary client plugin. Treat multiplayer networking and authority as explicit research topics.

## Research needed
Class and method mappings, exact interop assemblies, scene loading, network authority, and version-specific hooks must be sourced from the corresponding dumps, tests, or source repositories. See [research](../research/README.md).
