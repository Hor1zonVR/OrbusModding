#!/usr/bin/env python3
"""Cross-check curated dump symbols against Il2CppDumper script.json.

Usage: python tools/verify_il2cpp_signatures.py references/core-symbols.json script.json
No third-party Python packages required. Returns a nonzero exit code on mismatch.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("curated", type=Path)
    cli.add_argument("script_json", type=Path)
    args = cli.parse_args()
    data = json.loads(args.curated.read_text(encoding="utf-8"))
    symbols = json.loads(args.script_json.read_text(encoding="utf-8"))
    index = defaultdict(set)
    for item in symbols["ScriptMethod"]:
        index[item["Name"]].add(int(item["Address"]))
    matched = missing = mismatched = 0
    for cls in data["types"]:
        for method in cls["selected_methods"]:
            signature = method["signature"]
            method_name = signature.split("(", 1)[0].split()[-1]
            native_name = cls["namespace"] + "." + cls["name"] + "$$" + method_name
            addresses = index.get(native_name)
            if not addresses:
                missing += 1
                print("MISSING", native_name)
                continue
            rva = method.get("rva")
            if not rva or int(rva, 16) not in addresses:
                mismatched += 1
                print("MISMATCH", native_name, rva, sorted(addresses))
                continue
            matched += 1
    print(f"Matched: {matched}; missing: {missing}; address mismatches: {mismatched}")
    return 1 if missing or mismatched else 0

if __name__ == "__main__":
    sys.exit(main())
