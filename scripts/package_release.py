"""Deterministic relative-path archive + SHA256 manifest; excludes mutable local data.

Usage: python scripts/package_release.py /mnt/data/PFL_RELEASE.zip
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent.parent
IGNORE_DIR={'.pytest_cache','__pycache__','.git','.venv','htmlcov','demo'}
IGNORE_FILE={'.coverage','MANIFEST_SHA256.json'}

def all_files():
    return sorted((p for p in ROOT.rglob('*')
                   if p.is_file() and p.name not in IGNORE_FILE and not any(x in IGNORE_DIR for x in p.relative_to(ROOT).parts)
                   and p.suffix not in {'.pyc','.pyo'}),key=lambda p:str(p.relative_to(ROOT)))

def pack(target:Path):
    records={}
    paths=all_files()
    for p in paths:
        rel=p.relative_to(ROOT).as_posix()
        records[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    manifest={'release':'PFL_V0_4_BRANCH30_VSDS','date':'2026-10-25',
              'methodology':'AB 3.2.1', 'verified_tests':87,
              'evidence_state':'LOCAL_SYNTHETIC_PRODUCT_NO_VALIDATED_REAL_POLITICAL_SCORING',
              'github_published':True,'github_hosting':'TEMPORARY_IN_Metodologia-AB','files':records}
    manifest_path=ROOT/'MANIFEST_SHA256.json'
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    target.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=8) as z:
        for p in paths:
            z.write(p,arcname=f'politics_fantasy_league/{p.relative_to(ROOT).as_posix()}')
        z.write(manifest_path,arcname='politics_fantasy_league/MANIFEST_SHA256.json')
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
