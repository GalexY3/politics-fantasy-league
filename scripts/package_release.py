"""Deterministic relative-path archive + SHA256 manifest; excludes mutable local data.

Usage: python scripts/package_release.py /mnt/data/PFL_RELEASE.zip
"""
from __future__ import annotations
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent.parent
IGNORE_DIR={'.pytest_cache','__pycache__','.git','.venv','htmlcov','demo'}
IGNORE_FILE={'.coverage','MANIFEST_SHA256.json','.DS_Store'}
LOCAL_DATA_DIRS={'raw','bronze','silver','gold','local_field','demo'}

def all_files(target=None):
    target = target.resolve() if target is not None else None
    def include(p):
        parts = p.relative_to(ROOT).parts
        lower = tuple(part.lower() for part in parts)
        name = p.name.lower()
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents if parent != ROOT):
            return False
        if not p.is_file() or (target is not None and p.resolve() == target):
            return False
        if any(part in IGNORE_DIR or part.endswith('.egg-info') for part in lower):
            return False
        if len(lower) >= 2 and lower[0] == 'data' and lower[1] in LOCAL_DATA_DIRS:
            return False
        return (name not in {item.lower() for item in IGNORE_FILE}
                and name != '.env' and not name.startswith('.env.')
                and p.suffix.lower() not in {'.pyc','.pyo','.key','.pem'})
    return sorted((p for p in ROOT.rglob('*') if include(p)),key=lambda p:str(p.relative_to(ROOT)))

def pack(target:Path):
    records={}
    paths=all_files(target)
    for p in paths:
        rel=p.relative_to(ROOT).as_posix()
        records[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    manifest={'release':'LOCAL_EXPORT','date':datetime.now(timezone.utc).date().isoformat(),
              'methodology':'AB 3.2.1', 'verified_tests':None,
              'evidence_state':'LOCAL_SYNTHETIC_PRODUCT_NO_VALIDATED_REAL_POLITICAL_SCORING',
              'files':records}
    target.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=8) as z:
        for p in paths:
            z.write(p,arcname=f'politics_fantasy_league/{p.relative_to(ROOT).as_posix()}')
        z.writestr('politics_fantasy_league/MANIFEST_SHA256.json',
                   json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    with ZipFile(target) as z:
        corrupt=z.testzip()
        if corrupt:raise RuntimeError('ZIP corrupt: '+corrupt)
        for rel,meta in records.items():
            if hashlib.sha256(z.read(f'politics_fantasy_league/{rel}')).hexdigest()!=meta['sha256']:
                raise RuntimeError('Content digest mismatch in ZIP: '+rel)
    return len(paths)+1,target.stat().st_size,hashlib.sha256(target.read_bytes()).hexdigest()

if __name__=='__main__':
    n,bytes_count,digest=pack(Path(sys.argv[1]))
    print(json.dumps({'files_in_zip':n,'zip_bytes':bytes_count,'zip_sha256':digest},indent=2))
