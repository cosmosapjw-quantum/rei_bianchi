#!/usr/bin/env python3
"""Verify a handoff's bytes and DAG structure, never scientific truth."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    for name,meta in manifest['files'].items():
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts: raise ValueError('UNSAFE_MANIFEST_PATH')
        path=ROOT/rel
        if path.is_symlink() or not path.is_file(): raise ValueError('MISSING_OR_SYMLINK:'+name)
        data=path.read_bytes()
        if len(data)!=meta['bytes'] or hashlib.sha256(data).hexdigest()!=meta['sha256']:
            raise ValueError('BYTE_IDENTITY_MISMATCH:'+name)
    nodes=json.loads((ROOT/'DAG.json').read_text())['nodes']
    by_id={n['id']:n for n in nodes}
    if len(by_id)!=len(nodes): raise ValueError('DUPLICATE_NODE')
    visited=set();active=set()
    def visit(key):
        if key in active:raise ValueError('DAG_CYCLE')
        if key in visited:return
        active.add(key)
        for parent in by_id[key]['requires']:visit(parent)
        active.remove(key);visited.add(key)
    for key in by_id:visit(key)
    for name in ['CONTRACT.json','HANDOFF.json','RECEIVER_CONTRACT.json','SOURCE_PINS.json','RESULTS.json']:
        json.loads((ROOT/name).read_text())
    print(json.dumps({'status':'PASS_IDENTITY_AND_DAG_ONLY','files':len(manifest['files']),'DAG_nodes':len(nodes),'scientific_truth_verified':False}))
if __name__=='__main__':main()
