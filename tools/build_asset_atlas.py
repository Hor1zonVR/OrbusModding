#!/usr/bin/env python3
"""Generate a local, metadata-only atlas from AssetRipper indexes.

Usage: py -3 tools/build_asset_atlas.py --images OrbusImageCatalogue.csv
           --collection Highsteppe_level5.txt --assets ExportedProject/Assets
           --out OrbusAssetAtlas

No model, texture, mesh, shader, prefab or scene contents are copied.
File-name classifications are unverified research leads, not runtime facts.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import os
from pathlib import Path
import re

SCENERY = re.compile(r"highsteppe|(^|[^a-z])hs[_-]|terrain|street|building|bridge|fountain|tree|dock|cave|water|wall|lod", re.I)
RIG = re.compile(r"mixamorig|(^|[^a-z])ik[-_]|rig|bone|hand|arm|head|finger|grip|weapon|sword|bow|wand|mallet|hammer|shield|player|avatar|wrist|elbow", re.I)
CLASS_HINTS = {
    "Bard": r"bard|mallet|instrument",
    "Runemage": r"runemage|mage|wand|rune",
    "Paladin": r"paladin|hammer",
    "Warrior": r"warrior|sword|shield",
    "Ranger": r"ranger|archer|bow|arrow",
    "Musketeer": r"musketeer|gunner|musket|orbhealer",
    "Scoundrel": r"scoundrel|pistol",
    "Shaman": r"shaman|totem|mask",
}

def hints(name):
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ").replace("-", " ")
    return ";".join(k for k, v in CLASS_HINTS.items() if re.search(v, normalized, re.I))

def category(folder):
    p = folder.lower().replace("\\", "/").strip("/")
    if p.startswith("resources/"): p = p[len("resources/"):]
    for prefix, label in (
        ("ui_icons/inv", "inventory-icons"),
        ("ui_icons/weapons_and_armors", "weapons-armour-art"),
        ("ui_icons/achievements", "achievements"),
        ("ui_icons/fieldnotes", "fieldnotes"),
        ("ui_icons/newui", "ui"),
        ("magicalactual/icons", "status-effects"),
        ("magicalactual/gear", "gear-art"),
        ("interactivemap", "map-art"),
    ):
        if p == prefix or p.startswith(prefix + "/"): return label
    return "general-texture-unclassified" if p.startswith("texture2d") else "other-art"

def write_csv(path, columns, records):
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def images_index(path):
    result = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for entry in csv.DictReader(stream):
            name = (entry.get("Name") or "").strip()
            if not name: continue
            folder = (entry.get("Folder") or "").strip().replace("\\", "/").strip("/")
            result.append(dict(name=name, folder=folder, relative_path=f"{folder}/{name}",
                               category=category(folder), class_hints=hints(Path(name).stem),
                               size_kb=entry.get("SizeKB", ""), confidence="filename-only"))
    return result

def collection_index(path):
    result = []
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as stream:
        for entry in csv.DictReader(stream, delimiter="\t"):
            kind = (entry.get("Class") or "").strip()
            if not kind: continue
            name = (entry.get("Name") or "").strip()
            is_object = kind == "GameObject"
            result.append(dict(path_id=(entry.get("Path ID") or "").strip(),
                               asset_type=kind, name=name, source_collection=path.stem,
                               scene_candidate="yes" if is_object and SCENERY.search(name) else "",
                               rig_weapon_candidate="yes" if is_object and RIG.search(name) else "",
                               class_hints=hints(name), confidence="AssetRipper-name-only"))
    return result

def project_index(assets):
    rows = []
    kinds = {".unity": "scene", ".prefab": "prefab", ".shader": "shader",
             ".fbx": "mesh-file", ".obj": "mesh-file", ".dae": "mesh-file", ".mat": "material-file"}
    special_dirs = {"mesh", "terraindata", "terrainlayer", "animationclip", "avatar", "gameobject"}
    for root, _, files in os.walk(assets):
        for filename in files:
            p = Path(root) / filename
            kind = kinds.get(p.suffix.lower())
            if p.suffix.lower() == ".asset" and p.parent.name.lower() in special_dirs:
                kind = "unity-asset"
            if kind:
                rows.append(dict(name=p.stem, relative_path=p.relative_to(assets).as_posix(),
                                 kind=kind, class_hints=hints(p.stem), confidence="file-path-only"))
    return sorted(rows, key=lambda r: (r["kind"], r["relative_path"].lower()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, help="OrbusImageCatalogue.csv")
    parser.add_argument("--collection", type=Path, help="AssetRipper level5 TSV")
    parser.add_argument("--assets", type=Path, help="Local ExportedProject/Assets directory")
    parser.add_argument("--out", type=Path, default=Path("OrbusAssetAtlas"))
    args = parser.parse_args()
    if not (args.images or args.collection or args.assets):
        parser.error("At least one input is required")
    args.out.mkdir(parents=True, exist_ok=True)
    summary = {"warning": "Filename and Path ID observations are not verified runtime APIs or prefab links.", "counts": {}}
    if args.images:
        data = images_index(args.images)
        write_csv(args.out / "icons.csv",
                  ["name", "folder", "relative_path", "category", "class_hints", "size_kb", "confidence"], data)
        summary["counts"]["images"] = len(data)
        summary["counts"]["image_categories"] = dict(collections.Counter(d["category"] for d in data))
    if args.collection:
        data = collection_index(args.collection)
        columns = ["path_id", "asset_type", "name", "scene_candidate",
                   "rig_weapon_candidate", "class_hints", "source_collection", "confidence"]
        write_csv(args.out / "scene_collection.csv", columns, data)
        obj = [r for r in data if r["asset_type"] == "GameObject"]
        write_csv(args.out / "replay_scene_candidates.csv", columns, [r for r in obj if r["scene_candidate"]])
        write_csv(args.out / "rig_weapon_candidates.csv", columns, [r for r in obj if r["rig_weapon_candidate"]])
        summary["counts"]["collection_entries"] = len(data)
        summary["counts"]["replay_scene_candidates"] = sum(bool(r["scene_candidate"]) for r in obj)
        summary["counts"]["rig_weapon_candidates"] = sum(bool(r["rig_weapon_candidate"]) for r in obj)
    if args.assets:
        if not args.assets.is_dir(): parser.error("Assets folder not found")
        data = project_index(args.assets)
        write_csv(args.out / "project_files.csv",
                  ["relative_path", "name", "kind", "class_hints", "confidence"], data)
        summary["counts"]["project_files"] = len(data)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["counts"], indent=2))
    print("Saved local metadata to:", args.out.resolve())

if __name__ == "__main__":
    main()
