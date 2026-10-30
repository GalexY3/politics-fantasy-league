#!/usr/bin/env python3
"""Stage1 only: inspect official Agenda JSON ZIP structural keys, no outcomes."""
import hashlib
import io
import json
import urllib.request
import zipfile
from urllib.parse import urlsplit

URL = 'https://data.assemblee-nationale.fr/static/openData/repository/17/vp/reunions/Agenda.json.zip'
MD5 = '97332eb327d19e22d42a2f639e754d87'
MAX_BYTES = 50_000_000
MAX_MEMBER = 250_000
MAX_SAMPLE = 32

def describe(blob):
    if not 100 < len(blob) <= MAX_BYTES:
        raise ValueError('ZIP_SIZE_LIMIT')
    actual_md5 = hashlib.md5(blob).hexdigest()
    if actual_md5 != MD5:
        raise ValueError('PUBLISHED_CHECKSUM_DRIFT:' + actual_md5)
    with zipfile.ZipFile(io.BytesIO(blob)) as f:
        names = [x for x in f.infolist() if x.filename.lower().endswith('.json')]
        keys = set()
        sampled = 0
        counts = {'compteRenduRef': 0, 'timeStampDebut': 0,
                  'organeReuniRef': 0, '@xsi:type': 0}
        for item in names:
            if sampled >= MAX_SAMPLE:
                break
            if item.file_size > MAX_MEMBER:
                continue
            with f.open(item) as fd:
                data = fd.read(MAX_MEMBER + 1)
            if len(data) > MAX_MEMBER:
                continue
            obj = json.loads(data.decode('utf-8-sig'))
            entry = obj.get('reunion', {}) if isinstance(obj, dict) else {}
            if not isinstance(entry, dict):
                continue
            keys.update(entry.keys())
            sampled += 1
            for col in counts:
                counts[col] += int(col in entry)
    return {'schema': 'pfl.abh25.c03.zip_metadata_only.v1',
            'status': 'PRIMARY_ORIGINAL_SCHEMA_ONLY',
            'source_sha256':hashlib.sha256(blob).hexdigest(),
            'source_bytes':len(blob),'publisher_md5_match':True,
            'json_members':len(names),'sampled_members':sampled,
            'reunion_keys':sorted(keys),
            'key_presence_sample':counts,
            'minute_texts_read':False,'petition_outcomes_read':False,
            'scientific_cycle_counted':0,'frame_selected':False}

def main():
    req=urllib.request.Request(URL,headers={'User-Agent':'PFL-metadata-only/0.1'})
    with urllib.request.urlopen(req,timeout=25) as r:
        if r.status != 200 or urlsplit(r.url).hostname != 'data.assemblee-nationale.fr':
            raise ValueError('INVALID_SOURCE_REDIRECT')
        blob=r.read(MAX_BYTES+1)
    print(json.dumps(describe(blob),ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
