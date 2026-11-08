#!/usr/bin/env python3
"""Locally audit a Ghidra batched export; emit metadata, never pseudocode.

Usage:
  python ghidra_export_audit.py Orbus_Batches.zip --dump dump.cs --output audit/
"""
import argparse
import collections
import csv
import json
import re
import zipfile
from pathlib import Path

HEADER = re.compile(
    r'^FUNCTION (\d+) / selected (\d+)\r?\n'
    r'Name: ([^\r\n]*)\r?\n'
    r'Entry VA: (0x[0-9a-fA-F]+)\r?\n'
    r'RVA: (0x[0-9a-fA-F]+)\r?\n'
    r'={60}\r?\n', re.M)
BATCH_FILE = re.compile(r'functions_(\d+)-(\d+)\.txt$', re.I)
DIRECT_CALL = re.compile(r'\b((?:thunk_)?FUN_180[0-9a-fA-F]{6,})\s*\(')
SEND = re.compile(r'\bFUN_1802f2910\s*\([^,\n]+,[^,\n]+,([^,\n]+),')
RVA_COMMENT = re.compile(r'\bRVA:\s*(0x[0-9A-Fa-f]+)')
CLASS = re.compile(r'\b(?:class|struct|interface)\s+([A-Za-z_][A-Za-z0-9_<>.,]*)')


def load_dump_mapping(path):
    """Best-effort managed RVA names; retain collisions and aliases."""
    if not path:
        return {}
    addresses = collections.defaultdict(list)
    namespace, type_name, pending = '', '', None
    with open(path, encoding='utf-8-sig', errors='replace') as source:
        for line in source:
            s = line.strip()
            if s.startswith('// Namespace:'):
                namespace = s.partition(':')[2].strip()
                pending = None
            cm = CLASS.search(s) if ('class ' in s or 'struct ' in s or 'interface ' in s) else None
            if cm and not s.startswith('//'):
                type_name = cm.group(1)
            match = RVA_COMMENT.search(s)
            if match and s.startswith('//'):
                pending = match.group(1).upper().replace('0X', '0x')
                continue
            if pending and '(' in s and ')' in s and not s.startswith('//'):
                qualified = (namespace + '.' if namespace else '') + type_name
                addresses[pending].append(qualified + ' :: ' + s)
                pending = None
            elif pending and s.startswith('}'):
                pending = None
    return addresses


def iter_functions(archive):
    infos = []
    for info in archive.infolist():
        match = BATCH_FILE.search(info.filename)
        if match:
            infos.append((int(match.group(1)), info))
    for _, info in sorted(infos, key=lambda pair: pair[0]):
        raw = archive.read(info).decode('utf-8-sig', errors='replace').replace('\r\n', '\n')
        headers = list(HEADER.finditer(raw))
        for i, match in enumerate(headers):
            end = headers[i + 1].start() if i + 1 < len(headers) else len(raw)
            body = raw[match.end():end]
            body = body.split('\nBATCH SUMMARY:', 1)[0]
            body = body.split('\nBATCH PARTIAL:', 1)[0]
            yield {
                'ordinal': int(match.group(1)),
                'name': match.group(3),
                'va': match.group(4).upper().replace('0X', '0x'),
                'rva': match.group(5).upper().replace('0X', '0x'),
                'body': body, 'source': Path(info.filename).name,
            }


def write_catalog(archive_path, out, dump=None):
    out.mkdir(parents=True, exist_ok=True)
    aliases = load_dump_mapping(dump)
    stats = collections.Counter()
    seen = set()
    fails = []
    with (zipfile.ZipFile(archive_path) as archive,
          (out / 'function_index.csv').open('w', newline='', encoding='utf-8') as func_fp,
          (out / 'call_edges.csv').open('w', newline='', encoding='utf-8') as edge_fp,
          (out / 'outgoing_component_calls.csv').open('w', newline='', encoding='utf-8') as rpc_fp):
        funcs, edges, rpcs = (csv.writer(f) for f in (func_fp, edge_fp, rpc_fp))
        funcs.writerow(['ordinal', 'rva', 'va', 'native_label', 'managed_candidates',
                        'status', 'code_chars', 'visible_call_sites', 'source_file'])
        edges.writerow(['caller_ordinal', 'caller_rva', 'callee_va', 'visible_calls'])
        rpcs.writerow(['caller_ordinal', 'caller_rva', 'component_method_id',
                       'literal_in_decompiler'])
        for f in iter_functions(archive):
            idx, rva, body = f['ordinal'], f['rva'], f['body']
            stats['parsed_functions'] += 1
            if idx in seen:
                stats['duplicate_ordinals'] += 1
            seen.add(idx)
            failed = '[DECOMPILATION FAILED]' in body or '[DECOMPILATION ERROR]' in body
            if failed:
                fails.append({'ordinal': idx, 'rva': rva})
                stats['failed'] += 1
            matches = DIRECT_CALL.findall(body[body.find('{') + 1:] if '{' in body else body)
            calls = collections.Counter('0x' + name.split('_')[-1].upper() for name in matches)
            for callee_va, count in calls.items():
                edges.writerow([idx, rva, callee_va, count])
            for raw in SEND.findall(body):
                raw = raw.strip()
                try:
                    numeric_id = int(raw, 0)
                except ValueError:
                    numeric_id = ''
                rpcs.writerow([idx, rva, numeric_id, raw])
                stats['outgoing_request_sites'] += 1
            funcs.writerow([idx, rva, f['va'], f['name'],
                            ' | '.join(aliases.get(rva, [])[:20]),
                            'failed' if failed else 'ok', len(body), len(matches), f['source']])
            stats['direct_call_pairs'] += len(calls)
            stats['visible_call_sites'] += len(matches)
            if aliases.get(rva):
                stats['functions_with_dump_mapping'] += 1
    report = dict(stats)
    report['failed_functions'] = fails
    report['source_archive_name'] = Path(archive_path).name
    report['dump_was_provided'] = bool(dump)
    report['caveats'] = [
        'One RVA may map to multiple managed methods or aliases.',
        'Only syntactically visible direct FUN_ calls are captured.',
        'A numeric RPC ID is component-scoped; no server authority is inferred.',
        'Code bodies are not redistributed by this tool.',
    ]
    (out / 'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('archive', help='ZIP of Ghidra functions_XXXXXX-YYYYYY.txt files')
    parser.add_argument('--dump', help='Optional matching IL2CPP dump.cs')
    parser.add_argument('--output', default='ghidra_audit', help='Metadata results folder')
    args = parser.parse_args()
    result = write_catalog(args.archive, Path(args.output), args.dump)
    print(json.dumps({key: val for key, val in result.items()
                      if key != 'failed_functions'}, indent=2))


if __name__ == '__main__':
    main()
