#!/usr/bin/env python3
"""Prepare an additive review projection of a sealed BASS_HE package."""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

T=Path('/workspace/scratch/7fd51143e473/e13c10_research_20261012')
R=T/'BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1'
D=T/'DELIVERY_E13C10_FINAL'
P=T/'GIT_REVIEW_PROJECTION'
P.mkdir(exist_ok=False)
prefix='research/e13c10_first_midpoint_bound_local_20261012'
manifest=json.loads((R/'PACKAGE_MANIFEST.json').read_bytes())
build=json.loads((D/'BUILD_RECEIPT.json').read_bytes())
kit=json.loads((T/'RECOVERY_KIT_E13C10_FINAL/RECOVERY_KIT_BUILD_RECEIPT.json').read_bytes())
items=dict(manifest['files'])
items['PACKAGE_MANIFEST.json']=build['package_manifest']
index=[]
for rel,pin in sorted(items.items()):
    reason=None
    if rel.startswith('dependencies/'):
        reason='Original dependency archive included in the COMPLETE backup.'
    elif rel.startswith('runs/') and rel.endswith('/RESULT.json'):
        reason='Full raw captured cells retained in the COMPLETE backup.'
    elif rel.endswith('CONTROL_RESULTS.json') and pin['bytes']>500000:
        reason='Large raw manufactured control payload retained in the COMPLETE backup.'
    elif rel.endswith('.zip'):
        reason='Explicit toy transport fixture archive retained in the COMPLETE backup.'
    row={'package_relative_path':rel,**pin,'included_in_Git':reason is None}
    if reason:row['omitted_reason']=reason
    else:
        data=(R/rel).read_bytes()
        assert len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],rel
        target=P/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    index.append(row)
external={
    'DELIVERY/BUILD_RECEIPT.json':D/'BUILD_RECEIPT.json',
    'DELIVERY/BASS_HE_E13C10_TRANSFER_MANIFEST.json':D/'BASS_HE_E13C10_TRANSFER_MANIFEST.json',
    'DELIVERY/BACKUP_LOCATIONS.json':D/'BACKUP_LOCATIONS.json',
    'DELIVERY/SMALL_BACKUP_LOCATIONS.json':D/'SMALL_BACKUP_LOCATIONS.json',
    'DELIVERY/ACTUAL_RESTORE_COMMAND_RECEIPT.json':D/'ACTUAL_RESTORE_COMMAND_RECEIPT.json',
    'DELIVERY/ACTUAL_RESTORE_RECEIPT.json':T/'RESTORED_E13C10_ATTEMPT01/RESTORE_RECEIPT.json',
    'DELIVERY/RECOVERY_KIT_BUILD_RECEIPT.json':T/'RECOVERY_KIT_E13C10_FINAL/RECOVERY_KIT_BUILD_RECEIPT.json',
    'DELIVERY/prepare_git_projection.py':Path(__file__),
}
for rel,source in external.items():
    target=P/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
meta={'schema':'bass-he-e13c10-git-review-projection-v1','created_utc':datetime.now(timezone.utc).isoformat(),
    'package_root':R.name,'git_prefix':prefix,'base_branch':'research/e13c9-signed-volterra-local-20261012',
    'base_commit':'b35891fc2063f6621a91d52968e67c768fecf563','base_tree':'2621403951625bd7b819901a5248fcc8f39a1343',
    'package_manifest':build['package_manifest'],'complete_archive':build['archive'],'complete_name':Path(build['archive_path']).name,
    'recovery_kit':kit['archive'],'package_files':index,
    'external_delivery_records':list(external),'projection_index_self_hash':'Excluded; remote Git blob verification binds this file.',
    'new_NCP_work_units':[],'scientific_invocations_by_projector':0,
    'policy':'Additive review projection. Omitted raw cells and dependency ZIPs remain exact-byte available through the complete backup; no regeneration needed.'}
(P/'GIT_PROJECTION_INDEX.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
files=[]
for p in sorted(P.rglob('*')):
    if not p.is_file():continue
    data=p.read_bytes();rel=p.relative_to(P).as_posix()
    rec={'path':prefix+'/'+rel,'mode':'100644','type':'blob','bytes':len(data),
         'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
    try:
        content=data.decode('utf-8')
        if '\0' in content:raise UnicodeError('binary NUL')
        rec.update({'encoding':'utf-8','content':content,'upload_as_blob':len(data)>200000})
    except UnicodeError:
        rec.update({'encoding':'base64','content':base64.b64encode(data).decode(),'upload_as_blob':True})
    files.append(rec)
payload={'repository_full_name':'cosmosapjw-quantum/BASS_HE','base_tree_sha':meta['base_tree'],'base_commit':meta['base_commit'],
         'branch':'research/e13c10-first-midpoint-bound-20261012','base_branch':meta['base_branch'],'prefix':prefix,'files':files}
dest=T/'E13C10_GIT_PAYLOAD.json';dest.write_text(json.dumps(payload,ensure_ascii=True,separators=(',',':')))
receipt={'status':'READY_FOR_ADDITIVE_GIT_OBJECTS','file_count':len(files),'projected_bytes':sum(f['bytes'] for f in files),
         'omitted_package_files':sum(not x['included_in_Git'] for x in index),'separate_blobs':sum(x['upload_as_blob'] for x in files),
         'payload_path':str(dest),'payload_bytes':dest.stat().st_size,'payload_ascii_characters':len(dest.read_text()),
         'payload_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'expected_files':[{k:v for k,v in x.items() if k not in ('content','upload_as_blob','encoding')} for x in files]}
(D/'GIT_PROJECTION_PREPARATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='expected_files'},indent=2))
