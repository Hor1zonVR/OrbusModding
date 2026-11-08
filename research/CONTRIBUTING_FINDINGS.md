# Contribute a verifiable OrbusVR modding discovery

We want findings that make modding easier for **everyone**—human mod authors and AI coding assistants—not an unreviewed archive of decompiled code.

## Before contributing

Read [research workflow](../docs/research-workflow.md), [eight-batch research standard](batch-research-standard.md), and [current progress manifest](../references/research-batches.json). Verify the relevant game build and check whether the topic already has a guide.

## Finding template (copy into your own new page or pull request)

**Title:** Human-readable name of the subsystem/behavior.

- **Game/client build and hash:** exact known identifier; use *unknown* when unavailable.
- **Source:** Ghidra, managed metadata, log or authorized runtime test.
- **Method:** namespace, class, method signature; snapshot **RVA**, native **VA** and current mapping.
- **Trigger:** which player input, lifecycle event, network callback or script invokes the behavior.
- **Call chain:** direct callers → current method → meaningful callees. Note when virtual/indirect calls may be missing.
- **State:** fields and GameObjects read/written; serialized data, persistence and reset behavior.
- **Authority:** client-only visuals, outgoing request, incoming replicated state, or confirmed server-owned result.
- **Test:** reproducible steps, expected behavior and the **observed** result; say *not tested* if static only.
- **Modding use:** safe, reversible extension opportunities, any known public reference implementation.
- **Confidence:** *mapped*, *static-traced*, *runtime-tested*, *inferred* or *unresolved*.
- **Unknowns:** what must be found before the method becomes actionable for an implementation.
- **Links:** other classes, related research pages and supporting public source.

## Good versus bad findings

**Good:** “`PlayerCharacter.FixedUpdate` checks the registered external camera’s distance and clears it above 75 units (RVA `0x378D50`, statically traced; freecam impact not yet tested).”

**Bad:** “The game’s entire render distance is 75m and changing this makes all distant terrain load.” The second claim does **not** follow from the code and should not be published.

**Good:** “The client sends a request with a component-scoped method ID, and no server acceptance has been demonstrated.”

**Bad:** “Method ID 12 lets players give themselves arbitrary loot.” A request send site is not an item-grant handler.

## Public content policy

Publish your own independent summaries, small method metadata tables, original mod examples and test procedures. Don't upload complete proprietary binaries, private servers, credentials, copyrighted full decompilation bodies, or other players' private logs. Link published, open-source mods rather than copying unknown-license code.

## For researchers without the original dump

The repository provides documented class names, RVAs, call chains, confidence labels and [a local audit tool](../tools/ghidra_export_audit_README.md). Full raw pseudocode is not in this public repository. That limitation is deliberate and should be disclosed to AI tools.
