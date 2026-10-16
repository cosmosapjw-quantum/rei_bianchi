#!/usr/bin/env python3
"""Package an explicitly ready stage; never infer scientific completion."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

UNIT = Path(__file__).resolve().parent
REPO = UNIT.parent.parent

def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage')
    parser.add_argument('--base', required=True)
    parser.add_argument('--files', nargs='+', required=True)
    args = parser.parse_args()
    stage = args.stage
    if stage not in [f'{p}{i}' for p in ('R', 'C') for i in range(1, 11)]:
        raise SystemExit('Explicit R1-R10 or C1-C10 stage required')
    state_file = UNIT / ('THEORY_STAGES.json' if stage.startswith('R') else 'CODING_STAGES.json')
    science = json.loads(state_file.read_text())
    evidence = next(s for s in science['stages'] if s['id'] == stage)
    if evidence['status'] != 'complete':
        raise SystemExit('Science owner has not marked requested stage complete')
    checkpoint_dir = UNIT / 'checkpoints'
    checkpoint_dir.mkdir(exist_ok=True)
    dag_path = UNIT / 'PROGRESS_DAG.json'
    dag = json.loads(dag_path.read_text()) if dag_path.exists() else {
        'schema_version': 1, 'unit_id': UNIT.name,
        'baseline_commit': args.base,
        'edges': [[f'{p}{i}', f'{p}{i+1}'] for p in ('R','C') for i in range(1,10)] + [['R10','C1']],
        'nodes': [{'id':f'{p}{i}', 'status':'pending', 'evidence_refs':[]} for p in ('R','C') for i in range(1,11)],
        'claim_boundary':'Mechanical progress mirrors owner evidence; no scientific admission by packaging.'}
    node = next(n for n in dag['nodes'] if n['id'] == stage)
    node.update(status='complete', evidence_refs=evidence.get('evidence_refs', []), checkpoint=f'checkpoints/{stage}.json')
    dag['current_stage'] = stage
    write_json(dag_path, dag)
    checkpoint = {'schema_version':1, 'stage':stage, 'base_commit':args.base,
        'owner_stage_fact': evidence, 'packaging_status':'PACKAGED',
        'native_solver_runs':0, 'heavy_data_reads':0,
        'raw_private_data':'Excluded; external historical backup references retain their original verification limits.'}
    record_path = checkpoint_dir / f'{stage}.json'
    write_json(record_path, checkpoint)
    paths = [REPO / p for p in args.files] + [dag_path, record_path, Path(__file__).resolve()]
    paths = sorted(set(paths))
    for path in paths:
        if not path.is_file() or not path.is_relative_to(REPO):
            raise SystemExit(f'Invalid explicit checkpoint file: {path}')
    manifest = {'stage':stage, 'files':[{'path':str(p.relative_to(REPO)), 'size_bytes':p.stat().st_size,
        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
    manifest_path = checkpoint_dir / f'{stage}_MANIFEST.json'
    write_json(manifest_path, manifest)
    archive = checkpoint_dir / f'REI_FULL005_PAIR_20261016_{stage[0]}{int(stage[1:]):02d}_v1.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in paths + [manifest_path]:
            info = zipfile.ZipInfo(str(path.relative_to(REPO)), (2026,10,16,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
    package = {'stage':stage, 'archive':str(archive.relative_to(REPO)), 'size_bytes':archive.stat().st_size,
        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'base_commit':args.base}
    write_json(checkpoint_dir / f'{stage}_PACKAGE.json', package)
    print(json.dumps(package))

if __name__ == '__main__':
    main()
