# Offline Ghidra export auditor

Use `ghidra_export_audit.py` to scan a privately held Ghidra batch ZIP without uploading or publishing game code.

### Windows PowerShell

```powershell
python tools/ghidra_export_audit.py "C:\OrbusResearch\Orbus_Batches.zip" --dump "C:\OrbusResearch\dump.cs" --output "C:\OrbusResearch\audit"
```

The `--dump` argument is optional. It must come from the **same game build** as the Ghidra export if you use it for native-to-managed names.

The tool writes `function_index.csv` (RVA, VA, name, matching IL2CPP signatures, errors), `call_edges.csv` (explicit native calls), `outgoing_component_calls.csv` (visible calls to the snapshot's `NetEntity.CallServerComponent` address) and `summary.json`.

No decompiled function bodies are included in the generated catalogues. Keep your input ZIP and proprietary dumps private unless you have redistribution rights.

### Caveats

- The script's outgoing-network pattern uses RVA `0x2F2910` from one specific unverified-build snapshot. Verify it before reusing on another build.
- The managed-name parser is deliberately best effort: type aliases, nested definitions, generic instantiations and overloaded/shared native methods need manual cross-checking.
- Direct call edges omit indirect dispatch and reflection. A method ID is meaningful only within its component.
- These catalogues speed up research; they do not automatically establish network authority, verified mod hooks or game mechanics.

See the [research standard](../research/batch-research-standard.md) and [Batch 03 networking report](../research/batch-03-server-and-network-contracts.md).