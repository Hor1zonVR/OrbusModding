# Getting started

OrbusVR modding in this community includes client-side BepInEx plugins, server-side extensions, and separate utilities. These are distinct deployment targets.

## Workflow
1. Determine the exact game/client build and mod loader used by the target installation.
2. Review [architecture](architecture.md) and the [public mod index](../references/open-source-mods.md).
3. Select a small existing public mod as a reference and inspect its actual project file, dependencies, and entry point.
4. Set up a local build against legally obtained dependencies from your own installation; do not commit game DLLs.
5. Implement the smallest testable feature, log initialization, and verify it in a dedicated test environment.
6. Add settings integration only after checking the currently implemented ModCore/RebornMenu contract.

## Templates
The starter project under [templates/basic-bepinex](../templates/basic-bepinex/README.md) is a **scaffold**, not a verified drop-in Orbus binary. Check the installed BepInEx version and interop setup before building.
