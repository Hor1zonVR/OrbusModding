# Cross-checking managed-looking and native IL2CPP symbols

We compared the [48-class curated reference](../references/core-symbols.json) against the **separately supplied** Il2CppDumper `script(2).json`. Every selected method had a matching native method name and RVA in the companion export.

| Check | Result |
| --- | ---: |
| Selected curated method entries checked | **585** |
| Matching `script.json` name and address | **585** |
| No corresponding native symbol found | **0** |
| Address mismatches | **0** |

This is **cross-file consistency**, not Ghidra behavioral verification, proof of safe runtime hooking, or an assertion that the game build is the latest. The two exports likely originate from the same dump session.

## Examples

| Managed-looking method | TypeDef | RVA |
| --- | ---: | --- |
| `MagicalActual.PlayerCharacter.SummonMount()` | 9656 | `0x384FD0` |
| `MagicalActual.PlayerCharacter.teleportPlayer(...)` | 9656 | `0x38F5A0` |
| `MagicalActual.PlayerAvatar.equipGear()` | 9643 | `0x34B1B0` |
| `MagicalActual.Bard.RegisterNoteHit(...)` | 9513 | `0x41EFC0` |
| `MagicalActual.Bard.SuperStatusChange(...)` | 9513 | `0x41F6D0` |
| `MagicalActual.Runemage.finishSpellCast()` | 9750 | `0x47D830` |
| `MagicalActual.Paladin.SuperStatusChange(...)` | 9621 | `0x334EC0` |
| `MagicalActual.OrbusNetManager.SendBinary(...)` | 10018 | `0x30C330` |
| `MagicalActual.NetEntity.CallServerComponent(...)` | 10029 | `0x2F2910` |
| `MagicalActual.InventoryManager.Open()` | 9843 | `0x3CD0C0` |

The exact parameter lists appear in [core-symbols.json](../references/core-symbols.json); Ghidra-oriented C signatures can be resolved from the local `script.json` by exact `Namespace.Type$$Method` name.

## Repeat the verification

With the locally generated `script.json` available:

```sh
python tools/verify_il2cpp_signatures.py references/core-symbols.json /path/to/script.json
```

This checks the selected methods' names and RVA addresses, returning an error for unresolved or mismatched entries. It intentionally does not upload or publish the local script export.

## Source fingerprint

- `dump(2).cs` SHA-256: `a20ae0b773fa2c37a736432e3227fb8f7fe934699879006e9c9f5873b75d54b0`
- `script(2).json` SHA-256: `bdb5959bf8ae37d9cb590924c941a89ab95436db3a5743a5684b423ba04d53c1`

Raw dumps and binaries are intentionally excluded from the public repository.
