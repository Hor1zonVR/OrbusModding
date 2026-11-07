# AI Agent Instructions — OrbusVR Modding

This repository is a navigation and research resource, **not** a substitute for checking actual game assemblies and current mod source.

## Start here
1. Read [README.md](README.md) and [docs/getting-started.md](docs/getting-started.md).
2. Identify whether the requested work is a client BepInEx plugin, server plugin, or external desktop tool.
3. Read [docs/architecture.md](docs/architecture.md), [docs/modcore-integration.md](docs/modcore-integration.md), and [references/open-source-mods.md](references/open-source-mods.md) as relevant.
4. Consult the linked live source repository for working code. Pin a commit when reproducing behavior.
5. For game internals, use [research/README.md](research/README.md). Never invent class names, signatures, offsets, hooks, or configuration APIs.
6. Document the exact client build, loader/runtime, dependencies, and test steps for every change.

## Evidence standards
- **Verified**: confirmed by a cited source file, symbol dump, or reproducible test; record the game build and evidence.
- **Observed**: reported in a log or experiment, not yet independently reproduced.
- **Hypothesis**: proposed explanation requiring validation.
- **Planned**: design only; not a supported API.

Never present a planned ModCore API as already implemented. Prefer minimal, reversible changes and clear compatibility boundaries. Do not embed proprietary game binaries, private keys, tokens, server credentials, or personal data in generated code or commits.

## Deliverables for a new mod
Explain installation, dependencies, build commands, expected behavior, compatibility, limitations, and a short manual test checklist. Do not assume a plugin is safe on third-party servers; respect server rules and permissions.
