# Basic BepInEx starter (scaffold)

This directory documents a minimal client plugin skeleton. **It has not yet been compiled or tested against an Orbus client.**

The correct plugin base class, BepInEx package, interop assemblies, and target framework depend on the client and loader build. Copying a generic Unity Mono plugin into an IL2CPP BepInEx installation may fail.

## Before implementing
1. Clone a known working public Orbus plugin from [the reference index](../../references/open-source-mods.md).
2. Inspect its .csproj and plugin entry point.
3. Copy its *verified* package and interop setup for the same game build.
4. Change plugin identity and implement only a log-on-load test.
5. Confirm load in BepInEx logs, then add your feature.

A compile-ready template will be added after validation against the current modding instance. This avoids shipping a broken example as a working SDK.
