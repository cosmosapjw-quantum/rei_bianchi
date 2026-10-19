#!/usr/bin/env python3
"""Check immutable parents, added Rust sources, reused evidence and archive payload."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=p.parse_args()
    root=args.root
    parents=json.loads((root/'contracts/PARENT_INPUT_SHA256.json').read_text())
    added=json.loads((root/'contracts/SOURCE_IDENTITY.json').read_text())['new_files']
    for name,expected in {**parents,**added}.items():
        assert digest(root/name)==expected,name
    reuse=json.loads((root/'contracts/REUSED_EVIDENCE_SHA256.json').read_text())['files']
    for record in reuse:assert digest(root/record['new_path'])==record['sha256'],record['new_path']
    full=root/'MANIFEST_SHA256.json'
    count=0
    if full.exists():
        for record in json.loads(full.read_text())['files']:
            target=root/record['path']
            assert target.stat().st_size==record['bytes'] and digest(target)==record['sha256'],record['path']
            count+=1
    print(json.dumps({'status':'PASS','parent_inputs':len(parents),'added_sources':len(added),
                      'reused_evidence':len(reuse),'archive_payloads_if_manifest_present':count}))


if __name__=='__main__':main()
