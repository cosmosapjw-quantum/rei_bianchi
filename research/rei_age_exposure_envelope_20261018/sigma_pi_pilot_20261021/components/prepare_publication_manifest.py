#!/usr/bin/env python3
"""Select only the two authorized Git paths; compute actual Git blob identities."""
import hashlib,json,re,stat
from pathlib import Path
PACKAGE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in PACKAGE.parents if (p/'CASE_PROVENANCE_LEDGER_INDEX.json').exists())
WORK=ROOT.parent
B='research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/'
U='research/rei_unified_sigma_pi_20261021/'
DENY_URL=re.compile(r'https?://[^\s"\'<>]*(?:X-Amz-Signature|access_token=|drive\.usercontent\.google|content\.dropboxapi|dl\.dropboxusercontent)[^\s"\'<>]*',re.I)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    entries={}
    def add(path,target):
        if not path.is_file():return
        if not target.startswith((B,U)):raise ValueError('OUTSIDE_AUTHORIZED_PATH:'+target)
        if '.private.' in path.name or '__pycache__' in path.parts:raise ValueError('PRIVATE_OR_CACHE_FILE_SELECTED')
        data=path.read_bytes()
        if path.suffix in {'.json','.md','.txt','.csv','.py','.sh'} and DENY_URL.search(data.decode('utf-8',errors='ignore')):raise ValueError('PRIVATE_DOWNLOAD_URL_SELECTED:'+str(path))
        mode='100755' if path.stat().st_mode&stat.S_IXUSR else '100644'
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        item={'path':target,'local_path':str(path.resolve()),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':blob,'mode':mode}
        if target in entries and entries[target]!=item:raise ValueError('TARGET_COLLISION:'+target)
        entries[target]=item
    for p in PACKAGE.iterdir():
        if p.is_file():add(p,B+p.name)
    for relative in ('vendor','verification','reviews'):
        for p in (PACKAGE/relative).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:add(p,B+str(p.relative_to(PACKAGE)))
    for p in (PACKAGE/'components').iterdir():
        if p.is_file():add(p,B+str(p.relative_to(PACKAGE)))
    for relative in ('results','components/results','z2_extension/results'):
        folder=PACKAGE/relative
        for p in folder.iterdir():
            if p.is_file() and p.suffix in {'.json','.csv'}:add(p,B+str(p.relative_to(PACKAGE)))
        for p in (folder/'controllers').glob('*.json'):add(p,B+str(p.relative_to(PACKAGE)))
    for p in (PACKAGE/'z2_extension').iterdir():
        if p.is_file():add(p,B+str(p.relative_to(PACKAGE)))
    for relative in ('z2_extension/verification','z2_extension/figures'):
        for p in (PACKAGE/relative).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:add(p,B+str(p.relative_to(PACKAGE)))
    for p in ROOT.iterdir():
        if not p.is_file() or p.name in {'CASE_PROVENANCE_LEDGER.json','CASE_PROVENANCE_LEDGER.csv','GIT_PUBLICATION_MANIFEST.json'}:continue
        if p.suffix in {'.json','.md','.py','.csv','.gz'}:add(p,U+p.name)
    for p in (ROOT/'independent_audit').iterdir():
        if p.is_file() and p.suffix in {'.json','.md'}:add(p,U+'independent_audit/'+p.name)
    for name,folder in [('D0D1',WORK/'recovery_backups/checkpoints/D0D1'),('D3',WORK/'recovery_backups/checkpoints/D3/20261021T104524Z')]:
        for filename in ('BACKUP_RECEIPT.json','FULL_READBACK.json','LOCAL_ARCHIVE_RECEIPT.json'):
            p=folder/filename
            if p.exists():add(p,U+'backup_receipts/'+name+'_'+filename)
    rows=[entries[k] for k in sorted(entries)]
    changed=[r['local_path'] for r in rows if sha(r['local_path'])!=r['sha256']]
    if changed:raise ValueError('SOURCE_CHANGED_DURING_MANIFEST:'+json.dumps(changed))
    binary=[r for r in rows if Path(r['path']).suffix in {'.png','.pdf','.gz'}]
    canonical=json.dumps([{k:r[k] for k in ('path','mode','bytes','sha256','git_blob_sha1')} for r in rows],sort_keys=True,separators=(',',':')).encode()
    result={'schema':'rei.git_publication_manifest.v1','expected_parent_head':'8b71c13e23202edfce1ee67fb2da552fefb9a583','allowed_prefixes':[B,U],'entries':rows,'summary':{'files':len(rows),'bytes':sum(r['bytes'] for r in rows),'binary_files':len(binary),'binary_bytes':sum(r['bytes'] for r in binary),'source_stable':True,'selected_entries_identity_sha256':hashlib.sha256(canonical).hexdigest()},'exclusions':['All per-case NPZ/raw and case directories remain in verified archives.','Nested publication directory, caches, private download metadata/URLs and duplicate backup tar/readbacks excluded.','Full uncompressed ledger JSON/CSV remain local/archive; publish lossless gzip copies plus index.','The manifest does not include itself, avoiding recursive selfhash.'],'actions_performed':'LOCAL_MANIFEST_ONLY_NO_REMOTE_WRITE'}
    out=ROOT/'GIT_PUBLICATION_MANIFEST.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'manifest_path':str(out),'manifest_sha256':sha(out),**result['summary']},indent=2))
if __name__=='__main__':main()
