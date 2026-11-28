from pathlib import Path
import hashlib,json,os,tarfile,subprocess
w=Path('/root/HE25_NCP_BIRTH_20261016');receipts=json.loads((w/'BACKUP_BLOCK_RECEIPTS.json').read_text());out=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
for provider in ['google_drive','dropbox']:
 dest=w/(provider+'_FULL_READBACK.tar.gz')
 with dest.open('xb') as f:
  for r in sorted([r for r in receipts if r['provider']==provider],key=lambda r:r['index']):
   p=Path(r['readback_path']);assert sha(p)==r['sha256']
   with p.open('rb') as src:
    for b in iter(lambda:src.read(1048576),b''):f.write(b)
  f.flush();os.fsync(f.fileno())
 assert sha(dest)=='203b0d4f7896722e3ad0065141dd729f509e40b5797e0d8063613026b9c58338'
 root=w/('RESTORED_'+provider);root.mkdir()
 with tarfile.open(dest) as t:t.extractall(root,filter='data')
 r=root/'HE25';m=json.loads((r/'RESTORATION_MANIFEST.json').read_text())
 for rec in m['records']:assert sha(r/rec['path'])==rec['sha256'],rec['path']
 assert sha(r/'he23_original_cli_981ad6dd')=='981ad6dde18be7951c6b0200a49e6482b0e6fae644437197375bdd18ced5eafe'
 bare=root/'bundle_verify.git';subprocess.run(['git','init','--bare',str(bare)],capture_output=True,check=True)
 v=subprocess.run(['git','-C',str(bare),'bundle','verify',str(r/'HE25_SOURCE_AND_RESULTS.bundle')],capture_output=True,text=True,check=True)
 out.append({'provider':provider,'archive_sha256':sha(dest),'bytes':dest.stat().st_size,'manifest_files_verified':len(m['records']),'standalone_bundle_verified':True,'content_commit':m['content_commit']})
 print(provider,'RESTORED',flush=True)
result={'schema':'he25.remote_restore.v1','status':'BOTH_CLOUDS_ACTUAL_DOWNLOAD_AND_RESTORATION_VERIFIED','restorations':out,'blocks':receipts,'receipt_scope':'Receipt produced after immutable content archive; no self-inclusion claim. Initial failed full upload and partial fragment attempts preserved locally, superseded by verified four-block backups.'}
p=w/'BACKUP_RECEIPT.json'
with p.open('x') as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
