#!/usr/bin/env python3
"""Bounded public Git raw-content readback; no retries and no remote writes."""
import argparse,concurrent.futures,datetime,hashlib,json,re,sys,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
ALLOWED=('research/rei_hheli_pilot_20261021/',)

def sha(data):return hashlib.sha256(data).hexdigest()
def read_one(entry,repository,commit,timeout):
    started=time.monotonic();path=entry['path'];url='https://raw.githubusercontent.com/'+repository+'/'+commit+'/'+urllib.parse.quote(path,safe='/')
    result={'path':path,'expected_bytes':entry['bytes'],'expected_sha256':entry['sha256'],'expected_git_blob_sha1':entry['git_blob_sha1'],'status':'FAILED','HTTP_status':None,'whole_body_read':False}
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'REI-scoped-public-source-readback/1','Accept-Encoding':'identity'})
        with urllib.request.urlopen(request,timeout=timeout) as response:
            result['HTTP_status']=response.status
            limit=entry['bytes']+1024;data=response.read(limit+1)
            if len(data)>limit:raise ValueError('REMOTE_BODY_EXCEEDS_MANIFEST_BOUND')
            result.update(bytes=len(data),whole_body_read=True,sha256=sha(data),git_blob_sha1=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
            result['status']='PASS' if response.status==200 and len(data)==entry['bytes'] and result['sha256']==entry['sha256'] and result['git_blob_sha1']==entry['git_blob_sha1'] else 'FAILED_IDENTITY'
    except Exception as exc:
        result['error']=type(exc).__name__+': '+str(exc)
        if isinstance(exc,urllib.error.HTTPError):result['HTTP_status']=exc.code
    result['elapsed_s']=time.monotonic()-started
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--commit',required=True);p.add_argument('--repo',default='cosmosapjw-quantum/rei_bianchi');p.add_argument('--workers',type=int,default=6);p.add_argument('--timeout',type=float,default=30.);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('commit must be the actual published40-character SHA')
    if not re.fullmatch('[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',a.repo):p.error('repo must be owner/name')
    if not 1<=a.workers<=6 or not 0<a.timeout<=60:p.error('workers must be1..6 and timeout must be0..60s')
    if a.output.exists():p.error('output is create-only; choose a fresh receipt path')
    started=time.monotonic();manifest_bytes=a.manifest.read_bytes();manifest=json.loads(manifest_bytes);entries=manifest['entries']
    if not all(e['path'].startswith(ALLOWED) and '..' not in Path(e['path']).parts for e in entries):p.error('manifest entry outside authorized two paths')
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        rows=list(pool.map(lambda e:read_one(e,a.repo,a.commit,a.timeout),entries))
    rows.sort(key=lambda r:r['path']);passed=sum(r['status']=='PASS' for r in rows);stable=a.manifest.read_bytes()==manifest_bytes
    receipt={'schema':'rei.public_git_raw_readback.v1','repo':a.repo,'commit':a.commit,'manifest_sha256':sha(manifest_bytes),'manifest_stable':stable,'selected_entries_identity_sha256':manifest['summary']['selected_entries_identity_sha256'],'scope':'Whole-byte public raw content SHA256 and actual Git blob SHA1; tree modes/parent are verified separately by root','workers':a.workers,'timeout_per_GET_s':a.timeout,'retries':0,'remote_mutations':0,'counts':{'planned':len(entries),'passed':passed,'failed':len(entries)-passed,'whole_bytes_verified':sum(r.get('bytes',0) for r in rows if r['status']=='PASS')},'status':'PASS' if stable and passed==len(entries) else 'FAIL','elapsed_s':time.monotonic()-started,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2));return 0 if receipt['status']=='PASS' else 2
if __name__=='__main__':sys.exit(main())
