#!/usr/bin/env python3
"""Index a local Il2CppDumper dump.cs without committing the source dump.

Usage: python tools/index_il2cpp.py dump.cs --output generated
Requires Python 3.9+ and only its standard library.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

CORE = """PlayerCharacter PlayerAvatar PlayerRig PlayerMount PlayerWand PlayerTool
PlayerClass PlayerCompass PlayerJournal PlayerPet PlayerTombstone Bard Runemage
Paladin Archer Orbhealer Shaman Barbarian Swordboard Gambler Fisher FishingRod
FishingLure Monster OrbusHealthBar DamageParams StatusEffectParams Potion
PotionAgingStation InventoryManager InventoryItem InventoryItemInstance
PlayerEntity OtherPlayerEntity NetEntity OrbusNetManager OrbusNetComponents
OrbusNetSelfSpawn Teleporter Portal DungeonShard TimedDungeonManager
WeaponAdjuster ToolController QuestInfo QuestMarker SpawnManager ScenePreloader
PlayerHouseFurniture Npc""".split()
TYPE = re.compile(r"\b(class|struct|interface|enum)\s+(.+?)\s*// TypeDefIndex: (\d+)")
PRIORITY = re.compile(
    r"Send|Net|Call|Spawn|Damage|Health|Get|Set|Teleport|Potion|Mount|Combat|"
    r"Class|Grip|Ability|Inventory|Tool|Player|Cast|Clip|Show|Hide|Release|"
    r"Update|Event|Signal|Summon|Position|Rig|Equip|Reset|Portal|Add|Move|"
    r"Register|Load|Hit|Death|Die|Att|Exp", re.I
)

def parse_dump(text):
    items = []
    namespace = section = ""
    current = None
    rva = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("// Namespace:"):
            namespace = line[len("// Namespace:"):].strip()
        match = TYPE.search(line)
        if match:
            if current:
                items.append(current)
            current = dict(type_id=int(match.group(3)), namespace=namespace,
                name=match.group(2).split(" : ")[0], kind=match.group(1),
                declaration=line.split(" // TypeDefIndex: ")[0], dump_line=lineno,
                fields=[], methods=[], properties=[])
            section = ""
            rva = None
            continue
        if not current:
            continue
        if line in ("// Fields", "// Methods", "// Properties"):
            section = line[3:]
            continue
        found_rva = re.match(r"// RVA: (0x[0-9A-Fa-f]+)", line)
        if found_rva:
            rva = found_rva.group(1)
        if not re.match(r"(public|private|protected|internal)\s", line):
            continue
        if section == "Fields" and re.search(r";\s*//\s*0x[0-9a-fA-F]+", line):
            current["fields"].append(line)
        elif section == "Properties" and "{" in line and "}" in line:
            current["properties"].append(line)
        elif section == "Methods" and re.search(r"\([^;]*\)\s*(?:\{\s*\}|;)$", line):
            current["methods"].append(dict(
                signature=re.sub(r"\s*\{\s*\}$", "", line).rstrip(";"), rva=rva))
    if current:
        items.append(current)
    return items

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("dump", type=Path)
    cli.add_argument("--output", type=Path, default=Path("generated"))
    cli.add_argument("--namespace", default="MagicalActual")
    args = cli.parse_args()
    raw = args.dump.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    records = [r for r in parse_dump(raw.decode("utf-8-sig"))
               if r["namespace"] == args.namespace]
    args.output.mkdir(parents=True, exist_ok=True)
    rows = ["type_id\tkind\tname\tbase_or_interfaces\tfields\tmethods\tproperties\tline_in_dump"]
    for r in records:
        base = r["declaration"].split(" : ", 1)[1] if " : " in r["declaration"] else ""
        rows.append("\t".join(map(str, (r["type_id"], r["kind"], r["name"],
            base, len(r["fields"]), len(r["methods"]), len(r["properties"]),
            r["dump_line"]))))
    (args.output / "magicalactual-types.tsv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8")
    curated = []
    for name in CORE:
        r = next((item for item in records if item["name"] == name), None)
        if not r:
            continue
        usable = [m for m in r["methods"] if not re.search(
            r"\.(?:ctor|cctor)\(|[<>]|\s(?:get_|set_)", m["signature"])]
        priority = [m for m in usable if PRIORITY.search(m["signature"])]
        selected = (priority + [m for m in usable if m not in priority])[:26]
        curated.append(dict(type_id=r["type_id"], name=r["name"],
            namespace=r["namespace"], declaration=r["declaration"],
            dump_line=r["dump_line"], field_count=len(r["fields"]),
            method_count=len(r["methods"]), properties_count=len(r["properties"]),
            selected_fields=r["fields"][:18], selected_methods=selected))
    data = dict(schema_version=1, source=args.dump.name, sha256=sha,
        build="unverified",
        notes="Metadata only; selected members, not behavioral validation. RVA build-specific.",
        types=curated)
    (args.output / "core-symbols.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(records)} {args.namespace} types; {len(curated)} curated classes; SHA-256 {sha}")
    print(f"Wrote indexes under {args.output}")

if __name__ == "__main__":
    main()
