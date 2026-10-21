#!/usr/bin/env python3
"""Prepare the final create-only archive after root supplies publication evidence."""
import argparse,datetime,hashlib,json,re,tarfile
from pathlib import Path
PACKAGE=Path(__file__).resolve().parents[1]
UNIFIED=next(p for p in PACKAGE.parents if (p/'CASE_PROVENANCE_LEDGER_INDEX.json').exists())
WORK=UNIFIED.parent

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def eligible(path):
    rel=path.relative_to(WORK)
    return path.is_file() and not any(part in {'publication','__pycache__','.matplotlib_cache','.git'} for part in rel.parts) and not path.name.endswith('.private.json') and not path.name.endswith(('.tar.gz','.tgz','.zip')) and not '.tmp.' in path.name

def main():
    a=argparse.ArgumentParser();a.add_argument('--reviewed-commit',required=True);a.add_argument('--publication-receipt',type=Path,required=True);args=a.parse_args();args.publication_receipt=args.publication_receipt.resolve()
    if not re.fullmatch('[0-9a-f]{40}',args.reviewed_commit):a.error('reviewed commit must be an actual40-character Git commit')
    if not args.publication_receipt.is_file():a.error('root publication receipt is required before packing')
    publication=json.loads(args.publication_receipt.read_text())
    if args.reviewed_commit not in json.dumps(publication):a.error('publication receipt does not bind the reviewed commit')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=WORK/'recovery_backups/checkpoints/FINAL'/stamp;out.mkdir(parents=True,exist_ok=False)
    entries={}
    def add(path,target):
        if eligible(path):entries[target]={'local_path':str(path),'archive_path':target,'size_bytes':path.stat().st_size,'sha256':sha(path)}
    for p in PACKAGE.rglob('*'):add(p,'repo_payload/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/'+str(p.relative_to(PACKAGE)))
    for p in UNIFIED.iterdir():
        if p.is_file():add(p,'unified/'+p.name)
    for p in (UNIFIED/'independent_audit').rglob('*'):add(p,'unified/independent_audit/'+str(p.relative_to(UNIFIED/'independent_audit')))
    # Central publication evidence may live outside UNIFIED locally.
    published=json.loads((UNIFIED/'GIT_PUBLICATION_MANIFEST.json').read_text())
    central_prefix='research/rei_unified_sigma_pi_20261021/'
    for entry in published['entries']:
        if entry['path'].startswith(central_prefix):
            add(Path(entry['local_path']),'unified/'+entry['path'][len(central_prefix):])

    for name,folder in [('D0D1',WORK/'recovery_backups/checkpoints/D0D1'),('D3',WORK/'recovery_backups/checkpoints/D3/20261021T104524Z')]:
        for filename in ('BACKUP_RECEIPT.json','FULL_READBACK.json','LOCAL_ARCHIVE_RECEIPT.json'):
            p=folder/filename
            if p.exists():add(p,'backup_evidence/'+name+'/'+filename)
    for rel in ('recovery_backups/laneB_recovered/RECOVERY_SNAPSHOT.json','recovery_backups/provider_metadata/LANEB_35_REUSE_MAP.json'):
        p=WORK/rel
        if p.exists():add(p,'recovery_evidence/'+p.name)
    add(args.publication_receipt,'PUBLICATION_RECEIPT.json')
    rows=[entries[k] for k in sorted(entries)]
    manifest={'schema':'rei.final_archive.v1','snapshot_utc':stamp,'reviewed_source_results_commit':args.reviewed_commit,'publication_receipt_sha256':sha(args.publication_receipt),'historical_A_raw':'Referenced by verified original archive in CASE_PROVENANCE_LEDGER_INDEX.json; not duplicated here','files':rows}
    mf=out/'MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');archive=out/('REI_UNIFIED_FINAL_20261021_'+stamp+'.tar.gz')
    with tarfile.open(archive,'x:gz') as t:
        for r in rows:t.add(r['local_path'],arcname=r['archive_path'],recursive=False)
        t.add(mf,arcname='MANIFEST.json',recursive=False)
    changed=[r['local_path'] for r in rows if sha(r['local_path'])!=r['sha256']]
    if changed:raise RuntimeError('SOURCE_CHANGED_DURING_PACK:'+json.dumps(changed))
    with tarfile.open(archive,'r:gz') as t:
        bad=[r['archive_path'] for r in rows if hashlib.sha256(t.extractfile(r['archive_path']).read()).hexdigest()!=r['sha256']]
    if bad:raise RuntimeError('ARCHIVE_BYTE_VERIFICATION_FAILED:'+json.dumps(bad))
    receipt={'archive_path':str(archive),'size_bytes':archive.stat().st_size,'sha256':sha(archive),'payload_files':len(rows),'source_stable':True,'all_member_SHA256_verified':True,'reviewed_commit':args.reviewed_commit,'provider_upload':'NOT_RUN_ROOT_OWNS_UPLOAD','archive_snapshot_time':stamp,'manifest_sha256':sha(mf)}
    (out/'LOCAL_ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
