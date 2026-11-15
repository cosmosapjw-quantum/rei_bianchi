"""Freeze completed recovery002 evidence once; package only the new segment."""
from pathlib import Path
import hashlib,json,tarfile,datetime,os

P=Path('/home/cosmosapjw/Dropbox/bianchi/rei_ax08_plus_recovery_20261115')
S=P/'SHEAR_PLUS_continuation_002'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
receipt=json.loads((P/'RUN_TERMINAL_RECEIPT.json').read_text())
assert receipt['exit_code']==0,receipt
ret=dict(l.split('=',1) for l in (S/'RETURN.txt').read_text().splitlines() if '=' in l)
assert ret['status']=='COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' and ret['result']=='Ok(())' and float(ret['a'])==.2
identity=sha(S/'source_identity.txt')
assert identity=='d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185'
build=json.loads((P/'BUILD_RECEIPT.json').read_text())
binary=P/'rust/rei_microphysics/target/release/examples/axbi_plus_recovery_002'
assert sha(binary)==build['binary_sha256']=='c16932bdd7a9fdb86c20d9ea3d8b08f897663874e1f1b6e35ea39fa3f2db3263'
wr=json.loads((S/'execution_wrapper_identity.json').read_text())
assert wr['new_binary_sha256']==build['binary_sha256']
info={'status':'NATIVE_COMPLETE_OBSERVED','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'history_sha256':sha(S/'history.csv'),'checkpoint_sha256':sha(S/'checkpoint.txt'),'return_sha256':sha(S/'RETURN.txt'),'source_identity_sha256':identity,'binary_sha256':build['binary_sha256'],'wrapper_identity_sha256':sha(S/'execution_wrapper_identity.json'),'terminal_receipt_sha256':sha(P/'RUN_TERMINAL_RECEIPT.json'),'terminal_exit_code':receipt['exit_code'],'terminal_accepted':int(ret['accepted']),'native_segment_wall_s':float(ret['segment_wall_s']),'launcher_wall_s':receipt['launcher_wall_s'],'raw_history_bytes':(S/'history.csv').stat().st_size,'allocation_sha256':sha(P/'ALLOCATION.json'),'original_case_cumulative_actual_cost':'UNKNOWN; preserved full prior reserve plus observed new debit','source_remote_path':str(S)}
info_path=P/'PLUS002_NATIVE_INFO.json'
assert not info_path.exists(),'No completed evidence overwrite'
info_path.write_text(json.dumps(info,indent=2)+'\n')
members=[(x,x.relative_to(P).as_posix()) for x in sorted(S.rglob('*')) if x.is_file()]
for name in ['ALLOCATION.json','BUNDLE_MANIFEST.json','BUILD_RECEIPT.json','PREFLIGHT_RECEIPT.json','SOURCE_CORPUS_MANIFEST.json','RUN_RESERVED.json','RUN_PROCESS.json','RUN_TERMINAL_RECEIPT.json','PLUS002_NATIVE_INFO.json','PLUS_LEDGER_SCAN.json','axbi_plus_recovery_002.rs','recovery_tool.py','scan_plus_ledgers.py','harvest_plus_completion.py']:
    members.append((P/name,name))
members.extend((x,x.relative_to(P).as_posix()) for x in sorted((P/'recovery_002_raw').rglob('*')) if x.is_file())
members.append((binary,'build/axbi_plus_recovery_002'))
manifest={'schema':'rei.axbi.plus002.backup_members.v1','scope':'Only newly completed recovery002 plus its exact source/execution evidence; original four-case archive is not copied.','members':[{'name':name,'bytes':f.stat().st_size,'sha256':sha(f)} for f,name in members]}
mp=P/'PLUS002_BACKUP_MEMBERS.json';mp.write_text(json.dumps(manifest,indent=2)+'\n');members.append((mp,mp.name))
archive=P/'rei_ax08_plus002_source_20261116.tar.gz';partial=archive.with_suffix(archive.suffix+'.partial')
assert not archive.exists() and not partial.exists()
with tarfile.open(partial,'w:gz',compresslevel=6) as tf:
    for f,name in members:tf.add(f,arcname=name,recursive=False)
os.rename(partial,archive)
summary={'status':'NEW_SEGMENT_BACKUP_CREATED','path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'member_manifest_sha256':sha(mp),'members':len(members),'native_info':info}
(P/'PLUS002_BACKUP_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
