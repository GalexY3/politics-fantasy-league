"""Read a SINGLE downloaded raw JSON and report STRUCTURE only.

This is intentionally schema-agnostic: never assume unnamed parliamentary JSON keys.
Do not publish names/identifiers or hash PII by accident; counts and paths only.
Memory O(input bytes), document input capped; inspect arrays without emitting values.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json

MAX_BYTES = 20 * 1024 * 1024


def profile_json(path: Path, max_depth: int = 12) -> dict:
    b = path.read_bytes()
    if len(b) > MAX_BYTES:
        raise ValueError('Pilot JSON exceeds 20MiB safety bound')
    v = json.loads(b)
    paths: Counter[str] = Counter()
    types: Counter[str] = Counter()
    array_lengths: dict[str, list[int]] = {}

    def visit(obj, prefix='$', depth=0):
        paths[prefix] += 1
        typ = type(obj).__name__
        types[typ] += 1
        if depth >= max_depth:
            return
        if isinstance(obj, dict):
            for k, value in obj.items():
                # Structural keys may be arbitrary user text; never export raw dynamic keys.
                key = str(k) if str(k).isidentifier() and len(str(k)) <= 64 and not any(c.isdigit() for c in str(k)) else '[key]'
                visit(value, f'{prefix}.{key}', depth+1)
        elif isinstance(obj, list):
            vals = array_lengths.setdefault(prefix, [])
            if len(vals) < 100:
                vals.append(len(obj))
            for item in obj[:100]:
                visit(item, f'{prefix}[]', depth+1)
    visit(v)
    return {'source_sha256': sha256(b).hexdigest(), 'bytes':len(b),
            'status':'STRUCTURE_ONLY_NOT_NORMALIZED',
            'root_type':type(v).__name__,
            'counts_by_value_type':dict(sorted(types.items())),
            'structure_paths_seen':dict(sorted(paths.items())),
            'array_sizes_sampled':{p:{'seen':len(x),'min':min(x),'max':max(x)} for p,x in sorted(array_lengths.items()) if x},
            'traversal_limits':{'depth':max_depth,'array_item_limit':100,'array_instances_per_path':100}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=profile_json(args.json_file)
    s=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output:
        args.output.write_text(s,encoding='utf-8')
    print(s)
if __name__=='__main__': main()
