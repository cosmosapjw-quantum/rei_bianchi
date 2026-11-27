#!/usr/bin/env python3
"""Verify saved HE36 identities and delivery metadata, without any science replay.

Uses Python standard library only. Does not import scientific modules, evaluate
moments, render, benchmark, integrate an IVP, or write to the package.
"""
from pathlib import Path
import argparse,csv,hashlib,json,sys

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-delivery',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parent
    manifest=json.loads((root/'SCIENCE_MANIFEST.json').read_text());errors=[]
    for row in manifest['files']:
        relative=Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            errors.append('unsafe manifest path: '+str(relative));continue
        p=root/relative
        if not p.is_file():errors.append('missing: '+str(relative));continue
        b=p.read_bytes()
        if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:
            errors.append('identity mismatch: '+str(relative))
    dag=json.loads((root/'DAG.json').read_text())
    completed=sum(n['status']=='complete' for n in dag['nodes'])
    delivered=sum(n.get('publication')=='published' and n.get('backup')=='acknowledged' for n in dag['nodes'])
    if completed!=dag['completed']:errors.append('DAG count mismatch')
    if len(dag['nodes'])!=20:errors.append('DAG is not the20-stage unit')
    expected=['R'+str(i) for i in range(1,11)]+['C'+str(i) for i in range(1,11)]
    if [n['id'] for n in dag['nodes']]!=expected:errors.append('stage order mismatch')
    if args.require_delivery and (completed!=20 or delivered!=20):errors.append('all20 stage deliveries required')
    ack_count=0
    for n in dag['nodes']:
        if n.get('publication')!='published':continue
        ap=root/'delivery'/(n['id']+'_ACK.json')
        if not ap.is_file():errors.append('missing stage ACK: '+n['id']);continue
        a=json.loads(ap.read_text());ack_count+=1
        if a['commit']!=n['commit'] or a['archive_sha256']!=n['archive_sha256']:
            errors.append('stage delivery identity mismatch: '+n['id'])
        if a['dropbox']['status']!='completed' or a['dropbox']['file']['file_id']!=n['dropbox_id']:
            errors.append('stage provider ACK mismatch: '+n['id'])
    with (root/'components/diagnostic/outputs/ccc_moments.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    if len(rows)!=129:errors.append('saved diagnostic row count mismatch')
    record=json.loads((root/'RUN_RECORD.json').read_text())
    if record['workflow_version']!='1.0.0' or record.get('approval_version')!='0.2':errors.append('workflow/approval mismatch')
    out={'schema':'he36.saved_payload_verification.v1','status':'FAIL' if errors else ('REUSED_COMPLETE_VERIFIED_PAYLOAD' if delivered==20 else 'PAYLOAD_VERIFIED_DELIVERY_PENDING'),'files_verified':len(manifest['files']),'science_manifest_sha256':hashlib.sha256((root/'SCIENCE_MANIFEST.json').read_bytes()).hexdigest(),'stage_completed':completed,'stage_delivered':delivered,'stage_ACKs_checked':ack_count,'saved_CCC_rows':len(rows),'new_IVP':0,'new_render':0,'new_benchmark':0,'new_moment_evaluation':0,'new_scientific_test':0,'errors':errors}
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':sys.exit(main())
