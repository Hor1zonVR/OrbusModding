# Working with IL2CPP dumps and Ghidra

This workflow is specific to the kinds of files supplied for OrbusModding. It does **not** establish a stable IL2CPP SDK.

## Source files

| Input | What it provides |
| --- | --- |
| `dump.cs` | Managed-looking type declarations, fields, methods, TypeDef indices and RVAs |
| `script.json` | Native symbol names, C/C++ signatures and address mappings for Ghidra |
| `il2cpp.h` | Reconstructed native type layouts, pointers and some field structure |
| `stringliteral.json` | Literal strings with addresses; potentially noisy and sometimes sensitive |

The original raw files have **not** been uploaded to this public repository. See [snapshot provenance](../research/il2cpp-snapshot.md).

## Ghidra investigation checklist

1. Identify the exact game binary and metadata that generated the dump; record hashes and game/client build.
2. Locate a type/method in the [index](../references/magicalactual-types.tsv) and [curated symbols](../references/core-symbols.json).
3. Cross-check RVA and native signature in `script.json`. An RVA is relative to the binary image; the decompiler's displayed address depends on its image base.
4. Inspect the decompiled function, callers, and callees. Record meaningful evidence, not just a speculative interpretation of the name.
5. Compare managed-looking fields with `il2cpp.h` if a memory-layout assumption matters.
6. Confirm timing, lifecycle, network authority and input conditions in a controlled runtime test.
7. Document *what was observed* and what remains unknown. A method can be declared but unused, a stub, or version-dependent.

## Publishing a finding

Include **type and method**, **snapshot SHA-256**, **RVA**, **Ghidra evidence reference**, **runtime result**, **confidence**, **limitations**, and **related mod source**. Avoid sharing proprietary game binaries, unreviewed bulk dumps, credentials or users' data.

## About evidence labels

- **Dump verified**: name, signature or field exists in this specific dump.
- **Static analysis**: interpretation supported by documented decompiled control flow.
- **Runtime verified**: tested and reproduced in an identified game build.
- **Hypothesis**: requires further validation.

Never describe a dump-verified method as runtime-verified by default.
